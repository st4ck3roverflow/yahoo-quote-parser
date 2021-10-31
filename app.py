from flask import Flask, request, render_template

import yahoo_mod
from yahoo_mod import YahooParser
import os

os.environ["PATH"] += '/app/geckodriver'

print("[*] starting daemon")
updater_instance = yahoo_mod.YahooDaemon()
print("[+] created updater instance")
updater_instance.start()
print("[+] started updater instance")

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
                answ = yp_instance.read_from_db()
                if answ.startswith('err_'):
                    if answ == "err_readdb_operationerr":
                        return "404 Not Found"
                    else:
                        return "500 Internal Server Error"
                return answ


@app.route('/test')
def test_():
    import os

    return str(os.path.dirname(os.path.abspath(__file__)))


if __name__ == '__main__':
    app.run()
