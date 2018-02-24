import requests
import uuid
from xml.etree import ElementTree
from newspaper import Article as Parser
import spacy

CAT_MAP = {
    'sport': 'https://news.google.com/news/rss/headlines/section/topic/SPORTS.de_de/Sport?ned=de&hl=de&gl=DE',
    'technology': 'https://news.google.com/news/rss/headlines/section/topic/SCITECH.de_de/Wissen%20&amp;%20Technik?ned=de&hl=de&gl=DE',
    'entertainment': 'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT.de_de/Unterhaltung?ned=de&hl=de&gl=DE',
    'business': 'https://news.google.com/news/rss/headlines/section/topic/BUSINESS.de_de/Wirtschaft?ned=de&hl=de&gl=DE',
    'health': 'https://news.google.com/news/rss/headlines/section/topic/HEALTH.de_de/Gesundheit?ned=de&hl=de&gl=DE',
    'germany': 'https://news.google.com/news/rss/headlines/section/topic/NATION.de_de/Deutschland?ned=de&hl=de&gl=DE',
    'world': 'https://news.google.com/news/rss/headlines/section/topic/WORLD.de_de/International?ned=de&gl=DE&hl=de',
    'all': 'https://news.google.com/news/rss?ned=de&gl=DE&hl=de'
}


class ArticleFinder:

    def __init__(self):
        self.articles = {}
        for cat in CAT_MAP:
            self.articles[cat] = {}

    def lookup(self, category):
        r = requests.get(CAT_MAP[category])
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
