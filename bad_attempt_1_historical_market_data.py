import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

from clients import KalshiHttpClient, Environment

from datetime import datetime, timedelta
import time
import datetime
from datetime import datetime, timezone

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates







def setup():
    # Load .env values
    load_dotenv()

    # You can change this to Environment.PROD later if needed
    env = Environment.PROD

    # Get keys from environment
    KEYID = os.getenv("DEMO_KEYID") if env == Environment.DEMO else os.getenv("PROD_KEYID")
    KEYFILE = os.getenv("DEMO_KEYFILE") if env == Environment.DEMO else os.getenv("PROD_KEYFILE")

    # Load private key from PEM file
    with open(KEYFILE, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None  # Add password here if your PEM file is encrypted
        )

    # Initialize Kalshi HTTP client
    client = KalshiHttpClient(
        key_id=KEYID,
        private_key=private_key,
        environment=env
    )

    return client




def view_open_markets(client):
    markets = client.get("/trade-api/v2/markets")

    for market in markets["markets"]:
        title = market.get("title", "")
        if "trump" in title.lower() or "fed" in title.lower():
            volume = market.get("volume")
            ticker = market["ticker"]
            open_time_str = market.get("open_time")
            close_time_str = market.get("close_time")

            # ChatGPT: Parse ISO time to datetime objects
            open_time = datetime.fromisoformat(open_time_str.replace("Z", "+00:00"))
            close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            seconds_since_open = (now - open_time).total_seconds()

            print(f"Title: {title}")
            print(f"Ticker: {ticker}")
            print(f"Volume: {volume}")
            print(f"Open: {open_time} UTC")
            print(f"Close: {close_time} UTC")
            print(f"Time since open: {seconds_since_open:.0f} seconds ({seconds_since_open / 60:.1f} minutes)")
            print("-" * 50)

    return markets


def choose_market(client):

    ticker = "KXTRUMPMENTION-25MAY30-JAP"

    market_data = client.get(f"/trade-api/v2/markets/{ticker}")
    market = market_data["market"]

    print("Open:", market["open_time"])
    print("Close:", market["close_time"])

    trades = client.get_trades(ticker=ticker)

    print(f"Market: {market['title']}")
    for trade in trades["trades"]:
        created_time = datetime.fromisoformat(trade["created_time"].replace("Z", "+00:00"))
        print(f"Time: {created_time} | Side: {trade['taker_side'].upper():<3} | Count: {trade['count']:<3} | YES: {trade['yes_price']:>3}¢ | NO: {trade['no_price']:>3}¢")

    return trades

def plot_trades(trades):
    times = []
    yes_prices = []
    no_prices = []
    sizes = []

    for trade in trades["trades"]:
        t = datetime.fromisoformat(trade["created_time"].replace("Z", "+00:00"))
        times.append(t)
        yes_prices.append(trade["yes_price"])
        no_prices.append(trade["no_price"])
        sizes.append(trade["count"])  # for bubble size

    plt.figure(figsize=(10, 5))
    plt.plot(times, yes_prices, label="Yes Price", marker="o")
    plt.plot(times, no_prices, label="No Price", marker="x")
    plt.xlabel("Time")
    plt.ylabel("Price (cents)")
    plt.title("Kalshi Trade Prices Over Time")
    plt.legend()
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()





def main():
    client = setup()
    trades = choose_market(client)
    plot_trades(trades)


if __name__ == "__main__":
    main()