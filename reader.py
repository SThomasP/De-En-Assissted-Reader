from newspaper import Article
import string
from bs4 import BeautifulSoup


# A wrapper for newspaper, with some additional formatting and data extraction.
class ReadingAssistant:
    letters = string.ascii_letters + 'äöüßÄÖÜẞ'

    def __init__(self, article_url):
        article = Article(article_url, language='de')
        article.download()
        article.parse()
        self.article = article.text
        self.source = get_source(article.html)
        self.a_list = article_to_list(article.text)
        self.authors = article.authors
        self.title = article.title
        self.url = article.url


def get_source(html):
    soup = BeautifulSoup(html, 'html.parser')
    source_tag = soup.find('meta', property='og:site_name')
    source = source_tag['content']
    return source


def article_to_list(article):
    lines = article.splitlines()
    while '' in lines:
        lines.remove('')
    paragraphs = []
    for line in lines:
        parts = []
        word = True
        start_point = 0
        for i in range(len(line)):
            if (word and line[i] not in ReadingAssistant.letters) \
                    or (not word and line[i] in ReadingAssistant.letters):
                parts.append((word, line[start_point:i]))
                start_point = i
                word = not word
        paragraphs.append(parts)
    return paragraphs


