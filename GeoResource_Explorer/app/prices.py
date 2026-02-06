from flask import render_template
from app.db import get_db
from app.helpers import login_required
import requests, time, os

_price_cache = {'timestamp': 0, 'data': {}}
CACHE_TTL = 10*60

def price_routes(app):

    @app.route("/prices")
    @login_required
    def prices():
        if time.time() - _price_cache['timestamp'] < CACHE_TTL:
            prices = _price_cache['data']
        else:
            API_KEY = os.environ.get('METALS_API_KEY')
            metals = {'gold':'XAU','silver':'XAG','copper':'XCU'}
            prices = {}
            if API_KEY:
                for name, symbol in metals.items():
                    try:
                        r = requests.get(f'https://metals-api.com/api/latest?access_key={API_KEY}&symbols={symbol}&base=USD')
                        data = r.json()
                        prices[name] = data.get('rates', {}).get(symbol, 'N/A')
                    except:
                        prices[name] = 'Unavailable'
            else:
                prices = {'gold':'2000.00', 'silver':'25.20', 'copper':'4.10'}
            _price_cache['timestamp'] = time.time()
            _price_cache['data'] = prices
        return render_template("prices.html", prices=prices)
