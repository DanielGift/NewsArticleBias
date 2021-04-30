#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 16:53:28 2021

@author: danielgift
"""
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options
from newspaper import Config

#Puts limits on which authors to analyze; this allows the program
#to be run many times in parallel with different author subsets
#and allows saving in-between
print("Min ID:")
minidx = int(input())
print("Max ID:")
maxidx = int(input())
#Input validation
if minidx<1 or maxidx <=minidx:
    exit()
    
#Selenium infinite scrolling function taken from 
#https://dev.to/mr_h/python-selenium-infinite-scrolling-3o12
def scroll(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height
        
#User agent for selenium scraper
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10

#URL for allsides.com rating
URL = 'https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title='
options = Options()
options.set_preference('permissions.default.image', 2)
options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)

#The following 10 linies were also taken from 
#https://dev.to/mr_h/python-selenium-infinite-scrolling-3o12

# Setup the driver. This one uses firefox with some options and a path to the geckodriver
driver = webdriver.Firefox(options=options,executable_path=r"/usr/local/bin/geckodriver")
# implicitly_wait tells the driver to wait before throwing an exception
driver.implicitly_wait(5)
# driver.get(url) opens the page
driver.get(URL)
# This starts the scrolling by passing the driver and a timeout
scroll(driver, 3)
# Once scroll returns bs4 parsers the page_source
soup = BeautifulSoup(driver.page_source, 'lxml')
# Them we close the driver as soup_a is storing the page source
driver.close()

#This is original code
x = soup.findAll('table')[0].findAll('tr')
print("Number of authors: ",len(x))

links = [] #will store links to all articles we want to scrape
badNames = [] #Will store names of all authors we failt o scrape from

#Loop through the authors specified by the input indices
for i in x[max(1,minidx):maxidx]:
    y=i.findAll('td')
    if y != None:
        name = y[0].a.contents[0] #Name of author
        rawRating = y[1].a['href'] #url of image of rating
        #Convert rawRating into numerical rating:
        #2 for strong right bias, 1 for slight right bias, 0 for no bias
        #-1 for slight left bias, and -2 for strong left bias
        if rawRating == "/media-bias/left":
            rating = -2
        elif rawRating == "/media-bias/left-center":
            rating = -1
        elif rawRating == "/media-bias/center":
            rating = 0
        elif rawRating == "/media-bias/right-center":
            rating = 1
        elif rawRating == "/media-bias/right":
            rating = 2
        else: #if not one of the above, ignore this author
            continue
        print(name,rating)
        #Split into first and last name. This doesn't work perfectly, 
        #but we will deal with the failure cases later
        first, last = name.split(" ")[:2] 
        #Don't use data for cartoonists, as the cartoon medium doesn't 
        #lend itself well to this analysis
        if name.split(" ")[-1]=="(cartoonist)":
            continue
        #name part of url on muckrack.com, by default
        siteName = first.lower()+"-"+last.lower()
        page = 1 #will track which page of results we are on
        #Muckrack site with list of all articles by this author
        tosite = "https://muckrack.com/"+siteName+"/articles"
        mucksite = requests.get(tosite)
        #If this site doesn't exist, mark this author as a "badAuthor" and come back to later
        if mucksite.status_code == 404:
            print("Author not found by default")
            badNames.append(name)
            continue
        
        # Continue to look at later pages of results for articles this author wrote
        tosite = mucksite.url+"?page="
        soupMuck = BeautifulSoup(mucksite.content, 'html.parser')

        #This gets all the articles on this page
        articles = soupMuck.find_all("div", {"class": "news-story"})
        #Add the article link to the links list
        for art in articles:
            link = art.a["href"]
            links.append([last, first, link, rating])
        #This finds the button that says "see more"
        end = soupMuck.find_all("div", {"class": "endless_container"})
        #If it exists, we have another page to search for, so repeat
        while len(end) >= 1:
            page += 1 #Look at the next page
            if page%10 ==0: #Just to keep track of progress
                print("Reading page",page)
            mucksite = requests.get(tosite+str(page))
            soupMuck = BeautifulSoup(mucksite.content, 'html.parser')
            articles = soupMuck.find_all("div", {"class": "news-story"})
            for art in articles:
                link = art.a["href"]
                links.append([last, first, link, rating])
            end = soupMuck.find_all("div", {"class": "endless_container"})

#We now have an array of all the links to articles we want;
#Now we have to scrape those articles
data = [] #store all teh successfully scraped articles here
bads = [] #Store all the articles we unsuccessfully scraped here in case needed later
idx = 0 #keep track of progress
for ln, fn, lnk, rating in links:
    idx += 1
    if idx % 50 == 0: #Print progress
        print("Processed ", idx,"/",len(links)," articles")
    #Get the article in question
    atcl = Article(lnk,config=config)
    atcl.download()
    
    #Parse the url for the site domain
    sitex = re.search(r'(?<=https://www\.)\w+', lnk)
    if sitex== None:
        sitex = re.search(r'(?<=http://www\.)\w+', lnk)
    if sitex== None:
        sitex = re.search(r'(?<=https://)\w+', lnk)
    if sitex== None:
        sitex = re.search(r'(?<=http://)\w+', lnk)
    if sitex == None:
        print("Error parsing site: ",lnk)
        continue
    site = sitex.group(0)
    try:
        atcl.parse()
        text = atcl.text #Get article text
        data.append([ln, fn, site, text, rating, lnk]) #add to data list
    except:
        #If failed, add site into to bads list
        print("Error: ",site)
        bads.append([ln,fn,site,rating,lnk])
        continue
    
#Now save the data:
data = pd.DataFrame(data,columns=['lastName','firstName','Site','Text','Rating','URL'],index=range(len(data)))
data.to_csv('successfulArticleScrapes/ArticlesBias'+str(minidx)+".csv")
bads = pd.DataFrame(bads,columns=['lastName','firstName','Site','Rating','URL'],index=range(len(bads)))
bads.to_csv('uncuccessfulArticleScrapes/needToParse'+str(minidx)+'.csv')

#Save the badNames to a file to analyze later
with open('badNames/badNames'+str(minidx)+'.txt','w') as file:
    for name in badNames:
        file.write(name+"\n")