from flask import Flask, render_template, request
from dictionary import DictEntry
from reader import ReadingAssistant
import os



app = Flask(__name__)

'''
@app.route('/dict/json/<word>')
def json_lookup(word):
    entry = dictionary.lookup_json(word)
    return entry
'''


@app.route('/dict', methods=['POST'])
def html_lookup():
    word = request.form['word']
    lemma = request.form['lemma']
    tag = request.form['tag']
    dict_entry = DictEntry(word, lemma, tag)
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
