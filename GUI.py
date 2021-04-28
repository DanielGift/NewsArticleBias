#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 14:18:15 2021

@author: danielgift
"""

import tkinter as tk
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
import pickle
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
from time import time
from newspaper import Config
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
sw = (stopwords.words('english'))
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
import string
from tabulate import tabulate
import re
import tkinter.font as tkFont


window = tk.Tk()
i=100
fontBig = tkFont.Font(family="Lucida Grande", size=20)
fontSmall = tkFont.Font(family="Lucida Grande", size=12)
fontBold = tkFont.Font(family="Lucida Grande", size=12,weight='bold')
labeli = tk.Label(text="Welcome to the Article Bias Detector",font=fontBig)
label = tk.Label(text="Please enter the URL of a news article you would like to analyze the bias of:",font=fontSmall)
entry = tk.Entry(fg="black", bg="Gainsboro", justify='center', width=80)

def handle_click(event):
    print("The button was clicked!")

# button.bind("<Button-1>", handle_click)
labeli.pack()
label.pack()
entry.pack()


model = pickle.load(open('fullyTrainedModel.sav', 'rb'))
transModel = pickle.load(open('countVectorizerModel22.sav', 'rb'))
#User agent for selenium scraper
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10
# smallData = pd.read_csv("lemmatizedArticles.csv")
# trainAuthors = smallData.drop_duplicates("lastName")

#Tokenize and lemmatize the articles
lemmatizer = WordNetLemmatizer()
def lemmatize_text(text):
    lemmatized_sentence = []
    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+')
    tokens = tokenizer.tokenize(text)
    for word, tag in pos_tag(tokens):
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
        title = atcl.title
        author = atcl.authors
        lemtext = lemmatize_text(text)
        lemtextString = " ".join(lemtext)
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
        print("nopes")
        return None

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
    
def transformAll(link):
    toTransform = []
    transformedLinks = []
    transformedTitles = []
    transformedAuthors = []
    transformedSites = []
    isitin = []
    # for link in links:
    t1 = time()
    retval = getArticle(link)
    t2 = time()
    if retval != None:
        [lemtext, title, author, site] = retval
        toTransform.append(lemtext)
        transformedTitles.append(title)
        transformedAuthors.append(author)
        transformedSites.append(site)
        transformedLinks.append(link)
        # prevAut = ""
        # for aut in author:
        #     ln = aut.split(" ")[-1]
        #     isin = trainAuthors[trainAuthors['lastName']==ln]
        #     if len(isin)> 0:
        #         prevAut += "Yes "+aut+" "+str(isin["Rating"].values[0])
        # if len(prevAut) == 0:
        #     prevAut = "No"
        # isitin.append(prevAut)
    t3 = time()
    dflinks = pd.Series(toTransform)
    bagOfWords = transModel.transform(dflinks)
    predicted = model.predict(bagOfWords)
    categories = [translateScore(score) for score in predicted]
    totalDF = pd.DataFrame({'URL':transformedSites,'Rating':categories,"Title":transformedTitles,
                            "Author":transformedAuthors,"NewsSite":transformedSites})#,"IsDone":isitin})
    t4 = time()
    # print(t4-t3,t3-t2,t2-t1)
    return ([translateScore(predicted[0]),title])

inputLinks = ['https://www.newsbusters.org/blogs/nb/brent-bozell/2019/10/29/bozell-graham-column-media-cant-stand-trump-winning-ever'
,'https://www.breitbart.com/politics/2021/04/25/georgia-lawmakers-pass-professional-licenses-illegal-aliens-after-lobbying-chamber-commerce/'
,'https://www.breitbart.com/the-media/2020/06/26/blue-state-blues-alexis-de-tocqueville-saw-the-cancel-culture-coming/'
,'https://www.alternet.org/2018/08/mike-pence-once-argued-lying-cheating-president-should-be-removed-office-he/'
,'https://www.foxnews.com/opinion/biden-state-of-the-union-update-truth-president-sen-ted-cruz'
              ,'https://www.bbc.com/news/world-us-canada-56910884'
             ]
# result = transformAll(inputLinks)
# print((result.filter(['Title','Rating','IsDone',"Author"])))
def printRes():
    global i
    i += 1
    url = entry.get()
    [result,title] = transformAll(url)
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
    # label2.pack()
# button = tk.Button(text="Click me!")
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
