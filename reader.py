from newspaper import Article
import spacy

nlp = spacy.load('de')


# A wrapper for newspaper, with some additional formatting and data extraction.
class ReadingAssistant:

    def __init__(self, url, title):
        self.title = title
        self.url = url
        self.built = False
        self.article_model = None
        self.authors = None

    def build(self):
        if not self.built:
            self.built = True
            article = Article(self.url, language='de')
            article.download()
            article.parse()
            self.article_model = nlp(article.text)
            self.authors = article.authors
