import requests
import uuid
from xml.etree import ElementTree
from newspaper import Article as Parser
import spacy
import json
from csv import DictReader, DictWriter
from data import BAD_POS

# Load the Categories from a json file

with open("categories.json") as cat_file:
    CAT_MAP = json.load(cat_file)


class ArticleFinder:

    def __init__(self, fp):
        self.articles = {}
        self.fp = fp
        try:
            with open(fp, 'r') as csvfile:
                reader = DictReader(csvfile)
                for row in reader:
                    self.add_old_article(row)
        except FileNotFoundError:
            pass


    def lookup(self, category):
        r = requests.get(CAT_MAP[category]['url'])
        a_list = []
        root = ElementTree.fromstring(r.text)
        for item in root.iter('item'):
            url = item.find('link').text
            title = item.find('title').text
            aid = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
            article = Article(url, title, aid)
            a_list.append(article)
            if (aid not in self.articles) or (self.articles[aid] is None):
                self.articles[aid] = article
        self.save()
        return a_list

    def save(self):
        with open(self.fp, 'w') as csvfile:
            writer = DictWriter(csvfile, fieldnames=['article-id', 'url', 'title'])
            writer.writeheader()
            for article in self.articles:
                url = self.articles[article].url
                title = self.articles[article].title
                writer.writerow({'article-id': article, 'url': url, 'title': title})

    def add_old_article(self, article):
        aid = article['article-id']
        url = article['url']
        title = article['title']
        self.articles[aid] = Article(url, title, aid)

    def get_article(self, aid):
        return self.articles[aid]

    def get_article_list(self):
        return list(self.articles.keys())

    def articles_to_csv(self, fp):
        pass


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

    def build(self, dm):
        if not self.built:
            self.built = True
            article = Parser(self.url, language='de')
            article.download()
            article.parse()
            self.title = article.title
            self.article_model = nlp(article.text)
            self.authors = article.authors
            self.analyse(dm)

    def analyse(self, dm):
        if not self.built:
            self.build()
        for word in self.article_model:
            if word.pos_ not in BAD_POS:
                dm.log_article(self.id, word.text, word.lemma_)

if __name__ == '__main__':
    news = ArticleFinder()
    article = news.lookup('Wissen & Technik')[0]
