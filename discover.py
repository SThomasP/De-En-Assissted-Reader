import requests

CAT_MAP = {
    'SPORT': 'https://news.google.com/news/rss/headlines/section/topic/SPORTS.de_de/Sport?ned=de&hl=de&gl=DE',
    'TECHNOLOGY': 'https://news.google.com/news/rss/headlines/section/topic/SCITECH.de_de/Wissen%20&amp;%20Technik?ned=de&hl=de&gl=DE',
    'ENTERTAINMENT': 'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT.de_de/Unterhaltung?ned=de&hl=de&gl=DE',
    'BUSINESS': 'https://news.google.com/news/rss/headlines/section/topic/BUSINESS.de_de/Wirtschaft?ned=de&hl=de&gl=DE',
    'HEALTH': 'https://news.google.com/news/rss/headlines/section/topic/HEALTH.de_de/Gesundheit?ned=de&hl=de&gl=DE',
    'GERMANY': 'https://news.google.com/news/rss/headlines/section/topic/NATION.de_de/Deutschland?ned=de&hl=de&gl=DE',
    'WORLD':'https://news.google.com/news/rss/headlines/section/topic/WORLD.de_de/International?ned=de&gl=DE&hl=de',
    'ALL': 'https://news.google.com/news/rss?ned=de&gl=DE&hl=de'
}





class News:
    def lookup(self, category):
        pass
