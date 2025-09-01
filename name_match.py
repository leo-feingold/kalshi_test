import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
import pandas as pd

from clients import KalshiHttpClient, Environment


def get_client():

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

def experiment_data(client, limit = 1000, max_pages=100):

    all_markets = []
    cursor = None
    pages = 0
    params = {"status": "open"}

    while True:
        params["limit"] = limit
        if cursor:
            params["cursor"] = cursor

        print(f"Parsing Page {pages}.")
        resp = client.get("/trade-api/v2/markets", params=params)
        markets = resp.get("markets", [])
        cursor = resp.get("cursor")

        all_markets.extend(markets)
        pages += 1

        if not cursor or not markets or pages >= max_pages:
            break

    return {"markets": all_markets}


    #print(type(response))
    #print(response.keys())
    #print(type(response["markets"]))
    #print(type(response["markets"][0]))
    #print(response["markets"][0].keys())

def parse_market_names(response):
    markets = []

    for market in response["markets"]:
        market_ticker = market["ticker"]
        event_ticker = market["event_ticker"]
        title = market["title"]
        subtitle = market["subtitle"]
        yes_price = market["yes_ask"]
        no_price = market["no_ask"]
        yes_subtitle = market["yes_sub_title"]
        no_subtitle = market["no_sub_title"]


        markets.append({
            "event_ticker": event_ticker, 
            "title": title,
            "sub_title": subtitle,
            "market_ticker": market_ticker,
            "yes_subtitle": yes_subtitle,
            "no_subtitle": no_subtitle,
            "yes_price": yes_price / 100,
            "no_price": no_price / 100
            })

    return markets

def main():
    client = get_client()
    response = experiment_data(client)
    data = parse_market_names(response)
    
    df = pd.DataFrame(data)
    print(df.head())

    df.to_csv("kalshi_markets.csv", index=False)

if __name__ == "__main__":
    main()