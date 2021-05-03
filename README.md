# NewsArticleBias
*****************************************
**The short introduction to get started**
*****************************************
I have trained a machine learning model to recognize words that indicate left and right bias in news articles, using data from AllSides.com (https://www.allsides.com/media-bias/media-bias-ratings). This model is about 70% accurate, as can be seen in the ConfusionMatrix_NewsArticleBias.png file here. You can use this model to find out the bias of any news article by simply entering the URL of the article you want analyzed here: https://newsarticlebiasproject.ue.r.appspot.com/ ! Keep in mind, though, the model is only 70% accurate.

********************************************
**The long introduction to understand more**
********************************************

This is an ongoing project, so there are many places where I want to make changes, improvements, and updates! (README updated 4/30/21)

In today's increasingly polarized world, news media is essential to informing the public about what is happening in the world. Yet often peole can't even agree on facts because much of the information available on popular news sites comes through a biased, slanted lens. Often, especially among people who tend to consume media from only one or two sites, people don't even realize that the information they are consuming is biased, taking it as the truth and never even considering that the news source may be biased.
This is why efforts like those by AllSides Media are important. AllSides rates and evaluates a large host of articles and assigns a bias to various news sites, authors, and organizations. They assign one of 5 categories to each: Left, Lean Left, Center, Lean Right, and Right, representing sources that are stongly left-biased, somewhat left-biased, neither left nor right biased, slightly right biased, and strongly right biased, respectively. AllSides' ratings can be found here: https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=.
AllSides' methodology is rigorous and aims to eliminate bias (https://www.allsides.com/media-bias/media-bias-rating-methods). However, rating the bias of articles is an inherently subjective judgement. It is important to remember that this project is based on these subjective evaluations, and therefore carries with it the problems inherent in the initial evaluations. While AllSides' efforts are better than most, we shouldn't assume they are perfect (see disclaimers at the end).

What this project does is to scrape the data from AllSides related to bias evaluation of individual authors. We then assign AllSides' bias rating for that author to every article that author has written, under the assumption that individual authors tend to be pretty consistent in their bias lens. We scrape the text from all articles written by that author, utilizing the site https://muckrack.com/ to find a list of all articles they have written, and assign the rating of that author to all their articles. We then train a machine learning model to our data (over 210,000 articles from over 250 authors), which is able to correctly identify the bias rating for 70% of articles, as demonstrated in the ConfusionMatrix_NewsArticleBias.png file. We then deploy this model in a very basic web page where users can enter the URL of a news article, and the model will output its guess for the bias rating of the article. Users are encouraged to try out this web app for themselves here: https://newsarticlebiasproject.ue.r.appspot.com/

Below, I summarize in more detail the methodology. 

**********
**Step 1**
**********
Run scrapeAuthors.py. You will be prompted for a minimum and maximum index, because there are 329 authors scraped from https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=. By specifying indices less than 329, the program will only analyze the articles from authors between the min and max indices you specify, where the authors are ordered as on AllSides.com, by first name. This functionality is designed so you can run many iterations of scrapeAuthors.py in parallel. They will produce 3 files, each in their respective folders:
  1. ArticleBiasX.csv, where X is the first index used to generate this file, in folder successfulArticleScrapes: this is a csv file containing a DataFrame with columns for the article text, author, url, overarching site, and bias rating. Every successfully scraped article is in such a file.
  2. needToParseX.csv, where X is the first index used to generate this file, in folder unsuccessfulArticleScrapes: this is a csv file containing a DataFrame with columns for the name, rating, and url of every unsuccessfully scraped article. Unsuccessful scrapes often are the result of an article no longer being available, but storing the loist of unsuccessful scrapes is a useful catch mechanism in case I want to do more work to find some of these unsuccessfully found artciles.
  3. badNamesX.txt, where X is the first index used to generate this file, in folder badNames: this is a txt file listing the names of authors whose pages could not be found on muckrack.com. This is usually the result of:
      A. An improperly parsed name (e.g. 'Rev. Jesse Jackson Sr.'; since the parse takes the first 2 words as the first and last name, it would attempt to look for author Rev. Jesse)
      B. A non-typcal url (e.g. Andy Meek would be searched for at https://muckrack.com/andy-meek, but can actually be found at https://muckrack.com/tdnandy)
      C. The author not existing in the MuckRack database  (this happened in only a few instances). 
  We record these names in a txt file so that we can perform step 2, outlined below.

**********
**Step 2**
**********
From the list of bad authors generated in all of the files mentioned in point 3 above, manually search https://muckrack.com/ for the authors we were unable to automatically find. Copy the URLs of these authors from MuckRack into a local variable 'correctedURLs' in a new program, scrapeBads.py, modeled similarly to scrapeAuthors.py but with the additional variable 'correctedURLs'. This new variable is a list of lists, where each sublist contains an author's name, their MuckRack url, and their AllSides bias rating. We dropped a couple authors who could not be found on MuckRack. Using this list, generate, as in step 1, files ArticleBias2RoundX.csv and needToParse2RoundX.csv, which have the same structure as articleBiasX.csv and needToParseX.csv but are generated from the 'correctedURLs' list and so only include articles from authors not found on the first pass.

Run scrapeBads.py.

**********
**Step 3**
**********
Run combineArticles.py, which combines all the separate files form the separate runs from ArticleBiasX.csv and ArticleBias2RoundX.py and combines them into a single .csv file, allArticleData.csv

**********
**Step 4**
**********
Launch the BiasedMediaAnalyzer_part1.ipynb and run it. This is the first step in analyzing the data, and goes through the proccess of tokenizing and lemmatizing the text from the articles by reading in allArticleData.csv. Notably, the lemmatization keeps only adjectives, adverbs, interjections, verbs, and non-proper nouns. It ignores proper nouns as these are unlikely to show bias and are more likely to simply indicate subject, which is in and of itself not an indication of bias. All ofther parts of speech tend to carry fairly minimal uniqueness (e.g. propositions, pronouns) and are therefore ignored. The results of this file are saved as lemmatizedArticles.csv, to be read later. This csv file is largely the same as allArticleData.csv, except it also contains a column for the lemmatized version of the text and another column for the number of lemmatized tokens so we can ignore articles that aren't long enough to get much information from.

**********
**Step 5**
**********
Launch and run BiasedMediaAnalyzer_part2.ipynb. This reads in the lemmatized articles from lemmatizedArticles.csv, takes an equal number of each kind of article so as not to skew the ML model, creates a CountVectorizer for the lemmatized documents, and trains a Support Vector Classifier using an rbf kernel. The gamma and C parameters for this kernel are estimated by optimzing over a range of both, using a very small subset of the data (~3%) for this optimization, in the interest of speed. The actual training of the model had to be constrained to being trained on only 30% of the total corpus as training on the entire thing took too long, and this is an area in which I intend to improve. Nevertheless, as can be seen in the final tile of this file, or in the ConfusionMatrix_NewsArticleBias.png file, the model was able to correctly classify 70% of the test articles (a number which increases if we allow slight left articles to be misclassified as strong left articles, and vice versa, and same for slight right and strong right articles).

**********
**Step 6**
**********
Try it on your own article! You can either download the files and run the GUI.py file, a very basic file with a simple GUI that runs locally, or you can visit https://newsarticlebiasproject.ue.r.appspot.com/ (which will take a few seconds to load). Either way, you can enter a URL of a news article, and it will scrape the article and apply the trained ML model to determine its bias. Try it out yourself!

The files to run https://newsarticlebiasproject.ue.r.appspot.com/ are found in the simpleWebApp folder.

**********
**Step 7**
**********
I also wanted to get a sense of what was causing the algorithm to categorize different articles into the categories. As a first pass attempt to understand this (though I know there are many porblems with this), I analyzed which words have the highest difference between their occurrence frequency in the most frequent category compared to in the 2nd-most-frequent category, and identified these words as some of the more unique identifying words in the Bag Of Words Analysis. This revealed some interesting insights relating to topics of articles that lean in certain directions, as well as revealed some potential improvements to be made as some of the most unique words were related to the website (e.g. an advertisement or subscribe button) rather than the actual article content. Summaries of the most unique 8 words for each category can be found in the uniqueXX.png files (where XX = vr, sr, n, sl, or vl for articles that are Very Right Biased, Slightly Right Biased, Neutral, Slightly Left Biased, or very Left Biased, respectively), or in summary in MostImportantWords.pdf.

***************
**Disclaimers**
***************
The most notable disclaimer is that the model, as mentioned above, is 70% accurate. That means on any given article, 30% of the time you will be given a wrong classification. Therefore, take any individual article's rating with a grain of salt. What may be more helpful is to analyze a bunch of articles from a similar source, perhaps from the same website or from the same author (though you chould check first if they are already rated on AllSides.com!). If the majority of the articles come out with a similar rating, you can begin to conclude that that source may tend to produce articles with that rating. 

The second important disclaimer is, as mentioned at the beginning, these ratings are based on AllSides Media's inital rating of authors. This assumes that the rating are accurate, which is a subjective assessment. Furthermore, it assumes that all articles written by a particular author have the same bias rating, which may not in reality be true. While an author who is tends to write Strong Right Leaning pieces is unlikely to randomly write a Strong Left Leaning piece, they may write some articles that are Slightly Right Leaning or even Neutral every so often. Therefore, the initial categorization of the data fed into the model is not completely accurate.

Finally, this project is a work in progress. It started out as a proof-of-concept for my data analysis skills, and I want to continue improving and updating it. As of this version of the README, you are seeing the first public version, which is far from my first overall version, but is also hopefully far from the last public version.
