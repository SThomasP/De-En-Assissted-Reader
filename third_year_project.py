from flask import Flask, render_template, render_template_string, request, redirect
from dictionary import Dictionary
from reader import ReadingAssistant

app = Flask(__name__)

dictionary = Dictionary(config['oxford'])


@app.route('/dict/<word>')
def dict_lookup(word):
    entry = dictionary.lookup(word)
    return entry


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
