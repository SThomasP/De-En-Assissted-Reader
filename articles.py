import requests
import uuid
from xml.etree import ElementTree
from newspaper import Article as Parser
import spacy
import json

# Load the Categories from a json file

with open("categories.json") as cat_file:
    CAT_MAP = json.load(cat_file)


class ArticleFinder:

    def __init__(self):
        self.articles = {}
        for cat in CAT_MAP:
            self.articles[cat] = {}

    def lookup(self, category):
        r = requests.get(CAT_MAP[category]['url'])
        root = ElementTree.fromstring(r.text)
        for item in root.iter('item'):
            url = item.find('link').text
            title = item.find('title').text
            aid = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
            if aid not in self.articles[category]:
                self.articles[category][aid] = Article(url, title, aid)
        return self.articles[category]

    def get_articles(self, category, aid):
        return self.articles[category][aid]


nlp = spacy.load('de')


# A wrapper for newspaper, with some additional formatting and data extraction.
class Article:

    def __init__(self, url, title, id):
        self.title = title
        self.url = url
        self.id = id
        self.built = False
        self.article_model = None
        self.authors = None

    def build(self):
        if not self.built:
            self.built = True
            article = Parser(self.url, language='de')
            article.download()
            article.parse()
            self.article_model = nlp(article.text)
            self.authors = article.authors


if __name__ == '__main__':
    news = ArticleFinder()
    news.lookup('technology')
