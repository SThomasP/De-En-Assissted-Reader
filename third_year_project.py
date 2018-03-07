from flask import Flask, render_template, request, make_response,session, redirect
from dictionary import DictEntry
from articles import ArticleFinder, CAT_MAP
import os
import uuid

news = ArticleFinder()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/dict', methods=['POST'])
def html_lookup():
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    dict_entry = DictEntry(word, lemma, tag)
    return render_template("entry.html", entry=dict_entry)


@app.before_request
def check_for_session():

    def check_path(path):
        if path == '/':
            return True
        if path.startswith('/static/'):
            return True
        if path.startswith('/start') and request.method == 'POST':
            return True
        return False

    if 'user_id' not in session and not check_path(request.path):
        return redirect('/')


@app.route('/read/<article_id>')
def read_article(article_id):
    session['article_id'] = article_id
    article = news.get_article(article_id, session['cat'])
    response = make_response(render_template('article.html', article=article))
    return response


@app.route('/start', methods=['POST'])
def setup_session():
    session['cat'] = request.form['cat']
    session['level'] = request.form['level']
    session['user_id'] = uuid.uuid4()
    return redirect('/find')


@app.route('/find')
def find_articles():
    category = session['cat']
    articles = news.lookup(category,session['level'])
    return render_template('search.html', articles=articles, category=category)


@app.route('/')
def article_entry():
    cat_list = list(CAT_MAP.keys())
    cat_list.sort()
    return render_template('home.html', categories=CAT_MAP, cat_list=cat_list)


if __name__ == '__main__':
    app.run()
