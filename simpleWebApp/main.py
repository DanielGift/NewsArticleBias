from flask import Flask
from flask import request
import pandas as pd
import pickle
from newspaper import Article
from newspaper import Config
sw = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
import re
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

app = Flask(__name__)

@app.route("/")
def index():
    #Get url to analyze
    url = request.args.get("URL", "")
    if url:
        [rating,title] = detectBias(url)
    else:
        title = ""
        rating = ""
    #print the result only if there is a result to print
    if rating == "":
        return (
        """<form action="" method="get">
                Article URL: <input type="url" name="URL">
                <input type="submit" value="Detect Bias!">
            </form>""" 
            + """<br><br>"""+"This app created by Daniel Gift"+
            """<br>"""+"You can find the source code, along with a README with the appropriate disclaimers, "
            + """<a href=https://github.com/DanielGift/NewsArticleBias.git>here</a>"""
        )
    elif rating == "No detected bias":
        return (
        """<form action="" method="get">
                Article URL: <input type="url" name="URL">
                <input type="submit" value="Detect Bias!">
            </form>"""
        + "The article titled '" + title + "' has " + rating 
        + """<br><br>"""+"This app created by Daniel Gift"+
            """<br>"""+"You can find the source code, along with a README with the appropriate disclaimers, "
            + """<a href=https://github.com/DanielGift/NewsArticleBias.git>here</a>"""
        )
    else:
        return (
            """<form action="" method="get">
                    Article URL: <input type="url" name="URL">
                    <input type="submit" value="Detect Bias!">
                </form>"""
            + "The article titled '" + title + "' has a " + rating
            + """<br><br>"""+"This app created by Daniel Gift"+
            """<br>"""+"You can find the source code, along with a README with the appropriate disclaimers, "
            + """<a href=https://github.com/DanielGift/NewsArticleBias.git>here</a>"""
        )

#Load the ML models
model = pickle.load(open('fullyTrainedModel.sav', 'rb'))
transModel = pickle.load(open('countVectorizerModel.sav', 'rb'))
lemmatizer = pickle.load(open('Lemmatizer.sav', 'rb'))

#User agent for  scraper
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10


#Tokenize and lemmatize the articles
#Same lemmatization technique as when generating the training data
def lemmatize_text(text):
    global lemmatizer
    lemmatized_sentence = []
    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+')
    tokens = tokenizer.tokenize(text)
    for word,tag in pos_tag(tokens):
        #Only select adjectives, adverbs, interjections, verbs, or non-proper nouns
        #Proper nouns are unlikely to indicate bias (merely the subject), and other POS are generic and 
        #unlikely to be informative when it comes to bias determinations
        if tag.startswith('J') or tag.startswith('R') or tag.startswith('U') or tag.startswith('V') or tag=="NN" or tag =="NNS":
            if word not in "#$%&'()*+,-./:;<=>?@[\]^_`{|}~" and word not in '"' and word.lower() not in sw:
                lemmatized_sentence.append(lemmatizer.lemmatize(word.lower()))
    return lemmatized_sentence

def getArticle(link):
    #Get the article in question
    atcl = Article(link,config=config)
    atcl.download()
    try:
        atcl.parse()
        text = atcl.text #Get article text
        title = atcl.title #Get article title
        author = atcl.authors #Get article authors (will be a list)
        lemtext = lemmatize_text(text)
        lemtextString = " ".join(lemtext)
        #Get the first part of the website after the www.--this is the host site
        sitex = re.search(r'(?<=https://www\.)\w+', link)
        if sitex== None:
            sitex = re.search(r'(?<=http://www\.)\w+', link)
        if sitex== None:
            sitex = re.search(r'(?<=https://)\w+', link)
        if sitex== None:
            sitex = re.search(r'(?<=http://)\w+', link)
        if sitex == None:
            print("Error parsing site: ",link)
            return None
        site = sitex.group(0)
        return [lemtextString,title,author,site]
    except:
        print("error")
        return None

#Translate from numeric bias score to words
def translateScore(score):
    if score == -2:
        return "Strong Left bias"
    elif score == -1:
        return "Slight Left bias"
    elif score == 0:
        return "No detected bias"
    elif score == 1:
        return "Slight Right bias"
    elif score == 2:
        return "Strong Right bias"
    else:
        return "Indeterminate"
    
#Function to detect the bias of the article
def detectBias(link):
    toTransform = [] #Stores lemmatized text
    retval = getArticle(link)
    if retval != None:
        [lemtext, title, author, site] = retval
        toTransform.append(lemtext)
    dflinks = pd.Series(toTransform) #turn into Series to apply ML model
    bagOfWords = transModel.transform(dflinks) #transform
    predicted = model.predict(bagOfWords) #predict
    return ([translateScore(predicted[0]),title])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)