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

import pandas as pd



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



def view_events(client, limit: int = 20):
    response = client.get("/trade-api/v2/events", params={"status": "open"})
    events = response.get("events", [])[:limit]


    print(f"{'Ticker':<25} {'Category':<25} Title")
    print("-" * 80)
    for event in events:
        print(f"{event['event_ticker']:<25} {event['category']:<25} {event['title']}")


def view_markets(client, event_ticker = "KXNEXTUKPM-30"):
    response = client.get("/trade-api/v2/markets", params={"event_ticker": event_ticker})
    
    for market in response["markets"]:
        title = market.get("title", "")
        volume = market.get("volume")
        ticker = market["ticker"]
        open_time_str = market.get("open_time")
        close_time_str = market.get("close_time")

        # ChatGPT: Parse ISO time to datetime objects
        open_time = datetime.fromisoformat(open_time_str.replace("Z", "+00:00"))
        close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        seconds_since_open = (now - open_time).total_seconds()

        '''
        print(f"Title: {title}")
        print(f"Ticker: {ticker}")
        print(f"Volume: {volume}")
        print(f"Open: {open_time} UTC")
        print(f"Close: {close_time} UTC")
        print(f"Time since open: {seconds_since_open:.0f} seconds ({seconds_since_open / 60:.1f} minutes)")
        print("-" * 50)
        '''

    return response

def get_market_title(response, market_ticker = "KXNEXTUKPM-30-NF"):
    for market in response["markets"]:
        if market["ticker"] == market_ticker:
            market_title = market.get("title")

    return market_title


def get_all_trades(client, market_ticker = "KXNEXTUKPM-30-NF", max_trades=10_000):

    '''
    Getting trades using cursor parameter.
    '''


    all_trades = []
    cursor = None

    while True:
        response = client.get_trades(
            ticker=market_ticker,
            limit=1000,  # Max per page
            cursor=cursor
        )
        trades = response.get("trades", [])
        all_trades.extend(trades)

        # Stop if no more pages or hit max
        cursor = response.get("cursor")
        if not cursor or len(all_trades) >= max_trades:
            break

    print(len(all_trades))
    return all_trades


def view_trades(client, market_ticker = "KXNEXTUKPM-30-NF", n=10):

    trades = client.get_trades(ticker=market_ticker)

    print(len(trades["trades"]))

    '''
    print("\n")
    print(f"{'Time':<30} {'YES Price':<15} {'NO Price':<15} {'Count':<10} {'Taker Side'}")
    print("-" * 85)
    for t in trades["trades"][:n]:
        time_str = t['created_time']
        yes = t['yes_price'] / 100.0
        no = t['no_price'] / 100.0
        count = t['count']
        side = t['taker_side']
        print(f"{time_str:<30} {yes:<15.2f} {no:<15.2f} {count:<10} {side}")
    '''

    return trades


def plot_yes_price_over_time(trades, title):

    '''
    This looks at every trade and plots the yes price of that trade by date. 
    '''

    trades_list = trades["trades"]


    timestamps = [
        datetime.fromisoformat(t["created_time"].replace("Z", "+00:00"))
        for t in trades_list
    ]

    yes_prices = [t["yes_price"] / 100.0 for t in trades_list]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, yes_prices, marker='o', linestyle='-', alpha=0.8)
    plt.title(f"YES Price History for market: \n {title}")
    plt.xlabel("Time")
    plt.ylabel("YES Price ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_daily_close(trades, title):

    '''
    This looks at the closing yes price per day by date. 
    '''


    df = pd.DataFrame(trades["trades"])
    df["timestamp"] = pd.to_datetime(df["created_time"])
    df["yes_price"] = df["yes_price"] / 100.0
    df["date"] = df["timestamp"].dt.date

    # Keep only the last trade per day
    daily = df.sort_values("timestamp").groupby("date").last()

    plt.figure(figsize=(10, 5))
    plt.plot(daily.index, daily["yes_price"], marker='o', linestyle='-')
    plt.title(f"Daily Closing YES Price for market: \n {title}")
    plt.xlabel("Date")
    plt.ylabel("YES Price ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def main():
    client = setup()
    #view_events(client)
    response = view_markets(client)
    title = get_market_title(response)
    trades = view_trades(client)
    plot_yes_price_over_time(trades , title)
    #plot_daily_close(trades , title)



    

if __name__ == "__main__":
    main()