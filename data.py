import os

BAD_POS = ['AUX', 'ADP', 'CONJ', 'DET', 'INTJ', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SPACE', 'X']


class DataManager:
    def __init__(self, dir):
        self.user_lookups = os.path.join(dir, 'user_lookups.csv')
        self.article_words = os.path.join(dir, "article_words.csv")
        if not os.path.exists(self.user_lookups):
            with open(self.user_lookups, 'w') as csvfile:
                csvfile.write("user-id,article-id,word,lemma\n")
        if not os.path.exists(self.article_words):
            with open(self.article_words, 'w') as csvfile:
                csvfile.write("article-id,word,lemma\n")

    def log_user(self, user_id, article_id, word, lemma):
        with open(self.user_lookups, 'a') as csvfile:
            csvfile.write(
                "{user_id},{article_id}{word},{lemma}\n".format(user_id=user_id, article_id=article_id, word=word,
                                                                lemma=lemma))

    def log_article(self, article_id, word, lemma):
        with open(self.article_words, 'a') as csvfile:
            csvfile.write("{article_id},{word},{lemma}\n".format(article_id=article_id, word=word, lemma=lemma))
