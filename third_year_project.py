from flask import Flask, render_template, request, make_response
from dictionary import DictEntry
from articles import ArticleFinder, CAT_MAP
from data import DataManager, BAD_POS
import os
import uuid

dm = DataManager('usage_data')
app = Flask(__name__)
news = ArticleFinder('articles.csv')
app.secret_key = os.environ.get('SECRET_KEY')


@app.after_request
def set_user_id(response):
    if 'user_id' not in request.cookies:
        response.set_cookie('user_id', value=str(uuid.uuid4()), max_age=7776000, httponly=True)
    return response


@app.route('/dict', methods=['POST'])
def html_lookup():
    pos = request.form['pos']
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    user_id = request.cookies['user_id']
    article_id = request.cookies['article_id']
    if pos not in BAD_POS:
        dm.log_user(user_id, article_id, word, lemma)
    dict_entry = DictEntry(word, lemma, tag)
    return render_template("entry.html", entry=dict_entry)


@app.route('/read/<article_id>')
def read_article(article_id):
    article = news.get_article(article_id.lower())
    if not article.built:
        article.build(dm)
    response = make_response(render_template('article.html', article=article))
    response.set_cookie('article_id', value=article.id, max_age=3600, httponly=True)
    return response


@app.route('/find', methods=['POST'])
def find_articles():
    category = request.form['cat-selection']
    articles = news.lookup(category)
    return render_template('search.html', articles=articles, category=category)


@app.route('/')
def article_entry():
    cat_list = list(CAT_MAP.keys())
    cat_list.sort()
    return render_template('home.html', categories=CAT_MAP, cat_list=cat_list)


if __name__ == '__main__':
    app.run()
