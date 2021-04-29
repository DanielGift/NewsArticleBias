# NewsArticleBias

This is an ongoing project, so there are many places where I want to make changes, improvements, and updates!

In today's increasingly polarized world, news media is essential to informing the public about what is happening in the world and giving everyone the same facts to agree on. Yet the amount of biased or false information in the media has seemingly been increasing, and leading to divergent sets of facts that people on the political left and the political right are getting. Often, people don't even realize that the information they are consuming is biased, taking it as the truth and never even considering that the news source may be biased.
This is why efforts like those byt AllSides Media are important. AllSides consistently rates and evaluates a large host of articles and assigns a bias to various news sites, authors, and orgnaizations. They assign one of 5 categories: Left, Lean Left, Center, Lean Right, and Right, representing sources that are stongly left-biased, somewhat left-biased, neither left nor right biased, slightly right biased, and strongly right biased, respectively. AllSides' ratings can be found here: https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B2%5D=2&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=
AllSides' methodology is rigorous and aims to eliminate bias (https://www.allsides.com/media-bias/media-bias-rating-methods). However, rating the bias of articles is an inherently subjective judgement. It is important to remember that this project is based on these subjective evaluations, and therefore carries with it the problems inherent in the initial evaluations. While AllSides' efforts are better than most, we shouldn't assume they are perfect.

What this effort does is to scrape the data realted to bias evaluation of individual authors. We then assign AllSides' bias rating for that author to every article that author has written. We scrape the text from all articles written by that author, and assign the rating of that author to the article. We then train a machine learning model to our data (over 210,000 articles from over 300 authors), which is able to correctly identify the bias rating for the majority of articles! We then deploy this model in a very basic web page where users can enter the URL of a news article, and the model will output its guess for the bias rating of the article.

Below, I summarize in more detail the methodology. See also the comments in the code!
