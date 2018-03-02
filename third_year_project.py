from flask import Flask, render_template, request, session
from dictionary import DictEntry
from articles import ArticleFinder, CAT_MAP
from user import UserMap
import os


app = Flask(__name__)
news = ArticleFinder()
users = UserMap()
app.secret_key = os.environ.get('SECRET_KEY')


@app.before_request
def set_user_id():
    if "user_id" not in session:
        session['user_id'] = users.add_user()
        print('session id set')



@app.route('/dict', methods=['POST'])
def html_lookup():
    users.add_lookup(session['user_id'])
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    dict_entry = DictEntry(word, lemma, tag)
    return render_template("entry.html", entry=dict_entry)


@app.route('/read/<category>/<article_id>')
def read_article(category, article_id):
    users.set_reading(session['user_id'], article_id)
    article = news.get_articles(category, article_id.lower())
    if not article.built:
        article.build()
    return render_template('article.html', article=article)


@app.route('/find', methods=['POST'])
def find_articles():
    category = request.form['cat-selection']
    articles = news.lookup(category)
    a_list = list(articles.items())
    return render_template('search.html', articles=a_list, category=category)


@app.route('/')
def article_entry():
    cat_list = list(CAT_MAP.keys())
    cat_list.sort()
    return render_template('home.html', categories=CAT_MAP, cat_list=cat_list)


if __name__ == '__main__':
    app.run()
