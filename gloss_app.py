from flask import Flask, render_template, request, make_response,session, redirect
from dictionary import DictEntry
from articles import ArticleFinder, CAT_MAP
import os
import uuid
import logging

# load the article finder as well as the application framework
news = ArticleFinder()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# set up logging for the application
fh = logging.FileHandler('Gara.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(fmt='%(asctime)s [%(levelname)s]: "%(message)s"', datefmt='%Y-%m-%d %H:%M:%S'))
app.logger.addHandler(fh)


# Dictionary lookup, extract the information from the POST variables and create a dictionary entry based on them
@app.route('/dict', methods=['POST'])
def html_lookup():
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    app.logger.info("{user} has requested '{word}' on {article}.".format(user=session['user_id'], word=word, article=session['article_id']))
    dict_entry = DictEntry(word, lemma, tag)
    return render_template("entry.html", entry=dict_entry)


# make sure the user has a session_id
# and check to make sure they're not using the app out of order
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


# article view, show the user the contents of the requested article
@app.route('/read/<article_id>')
def read_article(article_id):
    session['article_id'] = article_id
    article = news.get_article(article_id, session['cat'])
    response = make_response(render_template('article.html', article=article))
    app.logger.info("{user} is reading article {count}  ({article}) which has a score of {readability}.".format(user=session['user_id'], article=article.id, count=session['count'] +1, readability=article.readability))
    return response


# the user's experience level and selected category is saved to their session information here
# the user is then redirected to the article listing view
@app.route('/start', methods=['POST'])
def setup_session():
    session.clear()
    session['cat'] = request.form['cat']
    session['level'] = request.form['level']
    session['count'] = 0
    session['user_id'] = uuid.uuid4()
    app.logger.info("{user} is at {level} level, reading {category} articles.".format(user=session['user_id'], level=session['level'], category=session['cat']))
    return redirect('/find')


# article listing view, show the user the articles in their selected category, along with their ratings
@app.route('/find')
def find_articles():
    if 'article_id' in session:
        aid = session.pop('article_id')
        app.logger.info("{user} has stopped reading {article}".format(user=session['user_id'], article=aid))
        session['count'] += 1
        # if the user has read three articles, reset their session
        if session['count'] == 3:
            return redirect('/finish')
    category = session['cat']
    articles = news.lookup(category, session['level'])
    return render_template('search.html', articles=articles, category=category)


# initial view, where the user inserts their preferred category and experience level
@app.route('/')
def article_entry():
    cat_list = list(CAT_MAP.keys())
    cat_list.sort()
    return render_template('home.html', categories=CAT_MAP, cat_list=cat_list)


# finish view, give the user a link to survey once they have read three articles
@app.route('/finish')
def finish_reading():
    user_id = session['user_id']
    return render_template('finish.html', user_id=user_id)


# reset the application for the next user
@app.route('/reset')
def reset_app():
    app.logger.info("{user} has stopped using the application".format(user=session['user_id']))
    session.clear()
    return redirect('/')


# run the application
if __name__ == '__main__':
    app.run()
