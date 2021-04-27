import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
import pandas as pd
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

#Hand-searched url's for many of the "badNames" whose MuckRack.com URL's were
#not found by default
correctedURLs = [
    ['Andy Meek',"https://muckrack.com/tdnandy/articles",-1],
    ['Bari Weiss',"https://muckrack.com/bariweiss/articles",0],
    ['Charles Blow',"https://muckrack.com/charlesmblow/artcles",-1],
    ['Christiane Amanpour',"https://muckrack.com/camanpour/articles",-1],
    ['Conor Friedersdorf',"https://muckrack.com/conor64/articles",0],
    ['David Petraeus',"https://muckrack.com/david-h-petraeus/articles", 0],
    ['Dr. Abdul El-Sayed',"https://muckrack.com/abdul-el-sayed/articles", -2],
    ['Eddie Scarry',"https://muckrack.com/escarry/articles", 2],
    ['Frank Bruni',"https://muckrack.com/frankbruni/articles",-1],
    ['George W. Bush',"https://muckrack.com/george-bush-1/articles",1],
    ['Glenn Greenwald',"https://muckrack.com/ggreenwald/articles", -1],
    ['Glenn Harlan Reynolds',"https://muckrack.com/glenn-harlan-reynolds/articles",1],
    ['H.R. McMaster',"https://muckrack.com/hr-mcmaster/articles", 0],
    ['Heather Mac Donald',"https://muckrack.com/heather-mac-donald/articles",2],
    ['Henry A. Brechter',"https://muckrack.com/henry-brechter/articles",0],
    ['James Mattis',"https://muckrack.com/james-n-mattis/articles", 0],
    ['Jeff Jacoby',"https://muckrack.com/jeff_jacoby/articles",2],
    ['Jennifer Rubin',"https://muckrack.com/jrubinblogger/articles",-1],
    ['Jeremy E Sherman',"https://muckrack.com/jeremy-e-sherman/articles",-1],
    ['Jim Geraghty',"https://muckrack.com/jimgeraghty/articles",1],
    ['Jim Rutenberg',"https://muckrack.com/jimrutenberg/articles",-1],
    ['Joe Scarborough',"https://muckrack.com/joenbc/articles",1],
    ['John R. Wood Jr.',"https://muckrack.com/john-wood-jr/articles",0],
    ['John Stossel',"https://muckrack.com/fbnstossel/articles",1],
    ['Jon Terbush',"https://muckrack.com/jonterbush/articles",-1],
    ['Jonah Goldberg',"https://muckrack.com/jonahnro/articles",2],
    ['Jonathan Miller',"https://muckrack.com/jonathan-miller-6/articles",-2],
    ['Jordan Weissmann',"https://muckrack.com/jhweissmann/articles",-2],
    ['Kimberley A. Strassel',"https://muckrack.com/kimberley-a-strassel/articles",2],
    ['Leana Wen',"https://muckrack.com/leana-s-wen/articles",-1],
    ['Marc A. Thiessen',"https://muckrack.com/marc-thiessen-1/articles",2],
    ['Mark Morford',"https://muckrack.com/markmorford/articles",-2],
    ["Mary O'Grady","https://muckrack.com/mary-ogrady/articles",2],
    ['Matt Drudge',"https://muckrack.com/drudge/articles",2],
    ['Maureen Dowd',"https://muckrack.com/nytimesdowd/articles",0],
    ['Neal K. Katyal',"https://muckrack.com/neal-katyal/articles",-1],
    ['Neil J. Young',"https://muckrack.com/neiljyoung17/articles",-1],
    ['Nicholas Kristof',"https://muckrack.com/nickkristof/articles",-2],
    ['Paul Volcker',"https://muckrack.com/paul-a-volcker/articles",0],
    ['Ramesh Ponnuru',"https://muckrack.com/rameshponnuru/articles",2],
    ['Rem Reider',"https://muckrack.com/rem-rieder/articles",0],
    [ 'Rev. Jesse Jackson Sr.',"https://muckrack.com/jesse-jackson-sr/articles",-2],
    ['Rich Lowry',"https://muckrack.com/richlowry/articles",2],
    ['Richard M. Cohen',"https://muckrack.com/richard-cohen-10/articles", -1],
    ['Russell Brandom',"https://muckrack.com/russellbrandom/articles",0],
    ['S.E. Cupp',"https://muckrack.com/s-cupp/articles", 1],
    ['Stacey Abrams',"https://muckrack.com/staceyabrams/articles",-1],
    ['Thomas L. Friedman',"https://muckrack.com/tomfriedman/articles",-1],
    ['Tim Pool',"https://muckrack.com/timcast/articles",0],
    ['Willam A. Galston',"https://muckrack.com/william-galston/articles",-1]
    ]

print(len(correctedURLs))
links = [] #will store links to all articles we want to scrape

#loop through names, using the input index bounds
for name, tosite, rating in correctedURLs[minidx:maxidx]:
    print(name, rating)
    page = 1
    #Get the muckrack page
    mucksite = requests.get(tosite)
    soupMuck = BeautifulSoup(mucksite.content, 'html.parser')

    #This gets all the articles on this page
    articles = soupMuck.find_all("div", {"class": "news-story"})
    #Parse the name--do it more carefully than last time
    nameParts = name.split(" ")
    #Jr. or Sr. endings are the only times when a last name is not the final word
    #in the above list
    #Assume first name is everything that isn't last name
    if nameParts[-1] not in ["Jr.","Sr."]:
        last = nameParts[-1]
        first = nameParts[0]
        for part in nameParts[1:-1]:
            first+=" " +part
    else:
        last = nameParts[-2]+" " + nameParts[-1]
        first = nameParts[0]
        for part in nameParts[1:-2]:
            first+=" " +part
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
        mucksite = requests.get(tosite+"?page="+str(page))
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
        print(lnk)
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
data.to_csv("successfulArticleScrapes/ArticlesBias2Round"+str(minidx)+".csv")
bads = pd.DataFrame(bads,columns=['lastName','firstName','Site','Rating','URL'],index=range(len(bads)))
bads.to_csv("unsuccessfulArticleScrapes/needToParse2Round"+str(minidx)+".csv")