import pandas as pd
import glob

#Function to find all files in the path pathToFiles that follow the RegEx 
#given by namePat
def readFiles(pathToFiles,namePat):
    procs = []
    #Identify all the available files
    for filename in glob.glob(pathToFiles+namePat):
        procs.append(filename)
    procs.sort()
    return procs

pTo = "successfulArticleScrapes/"
namePat = "ArticlesBias*.csv"
#Get list of filenames that match this
fileNames = readFiles(pTo,namePat)
print("Will be reading ",len(fileNames)," files")

countIt = 0 #Number of files read
totAuth = 0 #number of authors encountered
totArt = 0 #number of articles encountered
dfs = [] #list of all dataframes read in
for name in fileNames:
    temp = pd.read_csv(name)
    names = len(temp.groupby("lastName")) #Find how many names in this file
    articles = len(temp) #find how many articles in thsi file
    countIt += 1
    totAuth += names
    totArt += articles
    dfs.append(temp)
print("Total files read: ",countIt)
print("Total number of authors read: ",totAuth)
print("Total artciles read: ",totArt)
totData =pd.concat(dfs)
#Save all data
totData.to_csv("allArticleData.csv")