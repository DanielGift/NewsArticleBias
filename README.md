# NewsArticleBias

This is an ongoing project, so there are many places where I want to make changes, improvements, and updates!

In today's increasingly polarized world, news media is essential to informing the public about what is happening in the world and giving everyone the same facts to agree on. Yet the amount of biased or false information in the media has seemingly been increasing, and leading to divergent sets of facts that people on the political left and the political right are getting. Often, people don't even realize that the information they are consuming is biased, taking it as the truth and never even considering that the news source may be biased.
This is why efforts like those byt AllSides Media are important. AllSides consistently rates and evaluates a large host of articles and assigns a bias to various news sites, authors, and orgnaizations. They assign one of 5 categories: Left, Lean Left, Center, Lean Right, and Right, representing sources that are stongly left-biased, somewhat left-biased, neither left nor right biased, slightly right biased, and strongly right biased, respectively. AllSides' ratings can be found here: https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=
AllSides' methodology is rigorous and aims to eliminate bias (https://www.allsides.com/media-bias/media-bias-rating-methods). However, rating the bias of articles is an inherently subjective judgement. It is important to remember that this project is based on these subjective evaluations, and therefore carries with it the problems inherent in the initial evaluations. While AllSides' efforts are better than most, we shouldn't assume they are perfect.

What this effort does is to scrape the data realted to bias evaluation of individual authors. We then assign AllSides' bias rating for that author to every article that author has written. We scrape the text from all articles written by that author, and assign the rating of that author to the article. We then train a machine learning model to our data (over 210,000 articles from over 300 authors), which is able to correctly identify the bias rating for the majority of articles! We then deploy this model in a very basic web page where users can enter the URL of a news article, and the model will output its guess for the bias rating of the article.

Below, I summarize in more detail the methodology. Many of these codes took a very long time to run.

**********
**Step 1**
**********
Run scrapeAuthors.py. You will be prompted for a minimum and maximum index, because there are 329 authors scraped from https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=. By specifying indices less than 329, the program will only analyze the articles from authors between the indices you specify, where the authors are ordered as on AllSides.com, by first name. This functionality is designed so you can run many iterations of scrapeAuthors.py in parallel. They will produce 3 files, each in their respective folders:
  1. ArticleBiasX.csv, where X is the first index used to generate this file, in folder successfulArticleScrapes: this is a csv file containing a DataFrame with columns for the article text, author, url, overarching site, and bias rating. Every successfully scraped article is in such a file.
  2. needToParseX.csv, where X is the first index used to generate this file, in folder unsuccessfulArticleScrapes: this is a csv file containing a DataFrame with columns for the name, rating, and url of every unsuccessfully scraped article. Unsuccessful scrapes often are the result of an article no longer being available, but storing the loist of unsuccessful scrapes is a useful catch mechanism in case I want to do more work to find some of these unsuccessfully found artciles.
  3. badNamesX.txt, where X is the first index used to generate this file, in folder badNames: this is a txt file listing the names of authors whose pages could not be found on mukrack.com. This is usually the result of either A. an improperly parsed name (e.g. 'Rev. Jesse Jackson Sr.'; since the parse takes the first 2 words as the first and last nae, it would attempt to look for athro Rev. Jesse), B. a non-typcal url (Andy Meek would be searched for at muckrack.com/andy-meek, but can actually be found at muchrack.com/tdnandy), or C. The author not existing in the MuckRack page  (this happened in only a few instances). We record the names in a txt file so that we can perform step 2, outlined below.

**********
**Step 2**
**********
From the list of bad authors generated in all of the files mentioned in point 3 above, manually search muckrack.com for the authors we were unable to automatically find. Copy the URLs of these authors from muckrack.com into a local variable in a new program, scrapeBads.py, modeled similarly to scrapeAuthors.py but with an additional variable 'correctedURLs', which is a list of lists, where each sublist contains an author's name, their muckrack url, and their AllSides bias rating. We dropped a couple authors who could not be found on muckrack.com. Using this list, generate, as in step 1, files ArticleBias2RoundX.csv and needToParse2RoundX.csv, which have the same structure as articleBiasX.csv and needToParseX.csv but are generated from the 'correctedURLs' list and so only include articles from authors not found on the first pass.

Run scrapeBads.py

**********
**Step 3**
**********
run combineArticles.py, which combines all the separate files form the separate runs from ArticleBiasX.csv and ArticleBias2RoundX.py and combines them into a single .csv file, allArticleData.csv

**********
**Step 4**
**********
Launch the BiasedMediaAnalyzer_part1.ipynb and run it. This is the first step in analyzing the data, and goes through the proccess of tokenizing and lemmatizing the text from the articles. This is a slow process and takes a while to run over so many files. Notably, the tokenization keeps only adjectives, adverbs, interjections, verbs, and non-proper nouns. It ignores proper nouns as these are unlikely to show bias and are more likely to simply indicate subject, which is in and of itself not an indication of bias. All ofther parts of speech tend to carry fairly minimal uniqueness (e.g. propositions, pronouns) and are therefore ignored. The results of this file are saved as lemmatizedArticles.csv, to be read later. This csv file iis largely the same as allArticleData.csv, except it also contains a column for the lemmatized version of the text and one for the number of lemmatized tokens.

**********
**Step 5**
**********
Launch and run BiasedMediaAnalyzer_part2.ipynb. This reads in the lemmatized articles, takes an equal number of each kind of article so as not to skew the ML model, creates a CountVectorizer for the lemmatized documents, and trains a Support Vector Classifieer using an rbf kernel. the gamma and C parameters for this kernel are estimated by optimzing over a range of both, using a very small subset of the data for this optimization, in the interst of speed. The actual training of the model had to be constrained to 30% of the total corpus as training on the entire thing took too long, and this is an area in which I intend to improve. Nevertheless, as can be seen in the final tile of this file, the model was able to correctly classify 70% of the test articles (a number which increases if we allow slight left articles to be misclassified as strong left articles, and vice versa, and same for slight right and strong right articles.

**********
**Step 6**
**********
Try it on your own article! You can either download the files and run the GUI.py file, a very basic file with a simple GUI that runs locally, or you can visit https://newsarticlebiasproject.ue.r.appspot.com/ (which will take a few seconds to load). Either way, you can enter a URL of a news article, and it will scrape the article and apply the trained ML model to determine its bias. Try it out yourself!

The files to run https://newsarticlebiasproject.ue.r.appspot.com/ are found in the simpleWebApp folder.

***************
**Disclaimers**
***************
The most notable disclaimer is that the model, as mentioned above, is 70% accurate. That means on any given article, 30% of the time you will be given a wrong classification. Therefore, take any individual article's rating with a grain of salt. What may be more helpful is to analyze a bunch of articles from a similar source, perhaps from the same website or from the same author (though you chould check first if they are rated on ALlSides.com!). If the majority of the articles come out with a similar rating, you can begin to conclude that that source may tend to produce articles with that rating. 

The second important disclaimer is, as mentioned above, these ratings are based on AllSides Media's inital rating of authors. This assumes that the rating are accurate, whcih is a subjective assessment. Furthermore, it assumes that all articles written by a particular author have the same bias rating, which may not in reality be true. While an author wo tens towrite Storng Right pieces is unlikely to randomly write a Strong Left piece, they may write some that are slight right or even neutral. Therefore, the initial categorization of the data fed into the model is not completely accurate.

Finally, this project is a work in progress. It started out as a proof-of-concept for my data analysis skills, and I want to continue improving and updating it. As of this version of the README, you are seeing the first public version, which is far frrom my first overall version, but is also hopefully far from the last public version.


