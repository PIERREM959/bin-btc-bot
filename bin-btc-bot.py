import os
import time
import json
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"
TRADE_AMOUNT = 0.0001  # BTC
LOSS_THRESHOLD = 0.10  # 10%
CHECK_INTERVAL = 60 * 60  # 1h en secondes
STATE_FILE = "state.json"

client = Client(API_KEY, API_SECRET)

# === GESTION DE L'ÉTAT ===
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"position_open": False, "buy_price": 0.0, "highest_price": 0.0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

# === STRATÉGIE ===
def get_last_closes(n=4):
    candles = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1HOUR, limit=n)
    closes = [float(c[4]) for c in candles]  # prix de fermeture
    return closes

def get_current_price():
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    return float(ticker['price'])

def place_buy_order():
    try:
        order = client.order_market_buy(
            symbol=SYMBOL,
            quantity=TRADE_AMOUNT
        )
        print("Achat effectué :", order)
        return float(order['fills'][0]['price'])
    except BinanceAPIException as e:
        print("Erreur achat :", e)
        return None

def place_sell_order():
    try:
        order = client.order_market_sell(
            symbol=SYMBOL,
            quantity=TRADE_AMOUNT
        )
        print("Vente effectuée :", order)
    except BinanceAPIException as e:
        print("Erreur vente :", e)

# === BOUCLE PRINCIPALE ===
def run_bot():
    state = load_state()

    while True:
        print("\n=== Nouvelle itération ===")
        try:
            closes = get_last_closes()
            current_price = get_current_price()
            print(f"Clôtures H-3 à H : {closes}")
            print(f"Prix actuel : {current_price:.2f}")

            if not state["position_open"]:
                C0, C1, C2, C3 = closes[-1], closes[-2], closes[-3], closes[-4]
                if C0 > C1 and C0 > C2 and C0 > C3:
                    buy_price = place_buy_order()
                    if buy_price:
                        state = {
                            "position_open": True,
                            "buy_price": buy_price,
                            "highest_price": buy_price
                        }
                        save_state(state)
            else:
                if current_price > state["highest_price"]:
                    state["highest_price"] = current_price

                drawdown = 1 - (current_price / state["highest_price"])
                print(f"Plus haut atteint : {state['highest_price']:.2f} | Drawdown : {drawdown*100:.2f}%")

                if drawdown >= LOSS_THRESHOLD:
                    place_sell_order()
                    state = {
                        "position_open": False,
                        "buy_price": 0.0,
                        "highest_price": 0.0
                    }
                    save_state(state)

        except Exception as e:
            print("Erreur générale :", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
