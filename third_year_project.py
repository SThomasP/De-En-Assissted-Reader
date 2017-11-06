from flask import Flask, render_template, request
from dictionary import Dictionary
from reader import ReadingAssistant
import os

dict_config = {'app_id': os.environ.get('APP_ID'), 'app_key': os.environ.get('APP_KEY')}

app = Flask(__name__)
dictionary = Dictionary(dict_config)

'''
@app.route('/dict/json/<word>')
def json_lookup(word):
    entry = dictionary.lookup_json(word)
    return entry
'''


@app.route('/dict/html/<word>')
def html_lookup(word):
    dict_entry = dictionary.lookup_html(word)
    return render_template("entry.html", entry=dict_entry)


@app.route('/read')
def read_article():
    url = request.args['url']
    article = ReadingAssistant(url)
    return render_template('article.html', article=article)


@app.route('/')
def article_entry():
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
