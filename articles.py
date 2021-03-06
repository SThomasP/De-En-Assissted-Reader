import requests
import uuid
from xml.etree import ElementTree
from newspaper import Article as Parser
from newspaper import ArticleException
import textacy
import de_core_news_sm
import json


# the rankings for the various difficulty levels
RANKS = {'Beginner': [2, 3, 4, 5, 6, 7], 'Intermediate': [4, 5, 6, 7, 8, 9], 'Advanced': [6, 7, 8, 9, 10, 11],
         'Near Fluent': [8, 9, 10, 11, 12, 13]}

# Load the Categories from a json file

with open("categories.json") as cat_file:
    CAT_MAP = json.load(cat_file)


class ArticleFinder:

    # create the data structure for storing the articles
    def __init__(self):
        self.articles = {}
        for cat in CAT_MAP:
            self.articles[cat] = []

    # go through the articles in a list, classifying them based on the user's experience levels
    @staticmethod
    def classify(articles, level):
        to_return = []
        for a in articles:
            a_rep = {'id': a.id, 'title': a.title}
            read = a.readability
            ranks = RANKS[level]
            if read < ranks[0]:
                a_rep['rating'] = 'SL'
            elif read < ranks[1]:
                a_rep['rating'] = 'L'
            elif read < ranks[2]:
                a_rep['rating'] = 'ZL'
            elif read < ranks[3]:
                a_rep['rating'] = 'M'
            elif read < ranks[4]:
                a_rep['rating'] = 'ZS'
            elif read < ranks[5]:
                a_rep['rating'] = 'S'
            else:
                a_rep['rating'] = 'SS'
            to_return.append(a_rep)
        return to_return

    # get the articles in a category
    def lookup(self, category, user_level):

        # get the rss feed
        r = requests.get(CAT_MAP[category]['url'])
        root = ElementTree.fromstring(r.text)

        # get the old articles from memory
        old_aritcles = [a.id for a in self.articles[category]]

        # iterate through the article in the rss feed, extracting the articles
        for item in root.iter('item'):
            url = item.find('link').text
            title = item.find('title').text
            aid = str(uuid.uuid5(uuid.NAMESPACE_URL, url))

            # if the article is not already saved, try to parse and rate it (some articles fail)
            if aid not in old_aritcles:
                try:
                    self.articles[category].append(Article(url, title, aid, category))
                except ZeroDivisionError:
                    print('Zero Divison Error')
                except ArticleException:
                    print('Article Exception')

        # return the list of articles classified.
        return self.classify(self.articles[category], user_level)

    # get an individual article from a category list
    def get_article(self, aid, cat):
        cat_articles = self.articles[cat]
        article_ids = [a.id for a in cat_articles]
        index = article_ids.index(aid)
        return cat_articles[index]

# load in the German model
nlp = de_core_news_sm.load()


# A wrapper for newspaper, with some additional formatting and data extraction.
class Article:

    def __init__(self, url, title, id, category):
        self.title = title
        self.url = url
        self.id = id
        self.category = category
        self.article_model = None
        self.authors = None
        self.readability = 0
        self.build()

    # extract the article content an readability score
    def build(self):
        article = Parser(self.url, language='de')
        article.download()
        article.parse()
        self.title = article.title
        self.article_model = nlp(article.text)
        self.get_readability()
        self.authors = article.authors

    def get_readability(self):
        stats = textacy.TextStats(self.article_model)
        # Winer Sachtextformel https://de.wikipedia.org/wiki/Lesbarkeitsindex#Wiener_Sachtextformel
        self.readability = stats.wiener_sachtextformel


if __name__ == '__main__':
    news = ArticleFinder()
