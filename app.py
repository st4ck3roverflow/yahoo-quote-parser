from flask import Flask, request, render_template
import yahoo_mod

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/get_quote')
def get_quote():
    args = request.args
    if not args:
        return 'Ti pidoras'
    else:
        for i in args:
            if i == 'quote':
                return yahoo_mod.get_quote_json(args.get('quote'))


if __name__ == '__main__':
    app.run()
