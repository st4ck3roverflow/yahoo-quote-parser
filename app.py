from flask import Flask, request, render_template
from yahoo_mod import YahooParser

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/get_quote')
def get_quote():
    args = request.args
    if not args:
        return 'no_args'
    else:
        for i in args:
            if i == 'quote':
                yp_instance = YahooParser(args.get('quote'))
                yp_instance.get_quote()
                return yp_instance.parse_csv()


@app.route('/get_quote_selenium')
def get_quote_selenium():  # request answer await >20 sec
    args = request.args
    if not args:
        return 'no_args'
    else:
        for i in args:
            if i == 'quote':
                yp_instance = YahooParser(args.get('quote'))
                yp_instance.get_quote_selenium()
                return yp_instance.parse_csv()


if __name__ == '__main__':
    app.run()
