from flask import Flask, render_template, request
from dictionary import DictEntry
from articles import ArticleFinder, CAT_MAP


app = Flask(__name__)
news = ArticleFinder()


@app.route('/dict', methods=['POST'])
def html_lookup():
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    dict_entry = DictEntry(word, lemma, tag)
    return render_template("entry.html", entry=dict_entry)


@app.route('/read/<category>/<article_id>')
def read_article(category, article_id):
    article = news.get_articles(category.lower(), article_id.lower())
    if not article.built:
        article.build()
    return render_template('article.html', article=article)


@app.route('/find', methods=['POST'])
def find_articles():
    category = request.form['cat-selection']
    articles = news.lookup(category)
    a_list = list(articles.items())
    print(a_list)
    return render_template('search.html', articles=a_list, category=category)


@app.route('/')
def article_entry():
    cats = list(CAT_MAP.keys())
    cats.remove('all')
    cats.sort()
    return render_template('home.html', categories=cats)


if __name__ == '__main__':
    app.run()
