from newspaper import Article
import string
import spacy

nlp = spacy.load('de')


# A wrapper for newspaper, with some additional formatting and data extraction.
class ReadingAssistant:
    letters = string.ascii_letters + 'äöüßÄÖÜẞ'

    def __init__(self, article_url):
        article = Article(article_url, language='de')
        article.download()
        article.parse()
        self.article_model = self.build_model(article.text)
        self.authors = article.authors
        self.title = article.title
        self.url = article.url

    def build_model(self, text):
        model = nlp(text)
        return model

