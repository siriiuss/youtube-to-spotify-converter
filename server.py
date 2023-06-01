import os

from flask import Flask, render_template, request
import convert


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':
        url = request.form['yt-url']
        name = request.form['playlist-name']
        convert.convert(url, name)
        os.remove(".cache")
        return render_template('success.html')

    return render_template('form.html')


if __name__ == '__main__':
    app.run()