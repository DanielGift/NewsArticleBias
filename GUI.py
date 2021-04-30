import tkinter as tk
import pandas as pd
import pickle
from newspaper import Article
from newspaper import Config
from nltk.corpus import stopwords
sw = (stopwords.words('english'))
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
import string
import re
import tkinter.font as tkFont

#Set up the GUI
window = tk.Tk()
fontBig = tkFont.Font(family="Lucida Grande", size=20)
fontSmall = tkFont.Font(family="Lucida Grande", size=12)
fontBold = tkFont.Font(family="Lucida Grande", size=12,weight='bold')

labeli = tk.Label(text="Welcome to the Article Bias Detector",font=fontBig)
label = tk.Label(text="Please enter the URL of a news article you would like to analyze the bias of:",font=fontSmall)
entry = tk.Entry(fg="black", bg="Gainsboro", justify='center', width=80)

labeli.pack()
label.pack()
entry.pack()

#Load the ML models
model = pickle.load(open('simpleWebApp/fullyTrainedModel.sav', 'rb'))
transModel = pickle.load(open('simpleWebApp/countVectorizerModel.sav', 'rb'))
lemmatizer = pickle.load(open('simpleWebApp/Lemmatizer.sav', 'rb'))

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
            if word not in string.punctuation and word.lower() not in sw:
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

#Prints the result of the bias analyzer
def printRes():
    url = entry.get()
    [result,title] = detectBias(url)
    
    label2["text"]="The article titled "
    label3["text"]="'" +title+"'"
    if result == "No detected bias":
        label4["text"]="has"
    else:
        label4["text"]= ("has a ")
    label5["text"]=result
    if result == "Strong Right bias":
        label5['background']='Crimson'
    elif result == "Slight Right bias":
        label5['background']='LightCoral'
    elif result == "Strong Left bias":
        label5['background']='DodgerBlue'
    elif result == "Slight Left bias":
        label5['background']='LightBlue'
    else:
        label5['background']='LightGray'

button = tk.Button(
    text="Detect Bias",
    width=10,
    height=2,
    bg="gray",
    fg="black",
    command=printRes
)

button.pack()
label2 = tk.Label(text="",font=fontSmall)
label2.pack()
label3 = tk.Label(text="",font=fontBold)
label3.pack()
label4 = tk.Label(text="",font=fontSmall)
label4.pack()
label5 = tk.Label(text="",font=fontBig)
label5.pack()

window.mainloop()
