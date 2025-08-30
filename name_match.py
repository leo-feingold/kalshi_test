import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

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

def get_events(client):
    response = client.get("/trade-api/v2/events", params={"status": "open"})
    print(f"Example Data Point: {response['events'][0]}")
    return response

def parse_market_names(response):
    data = []
    for event in response["events"]:
        ticker = event["event_ticker"]
        title = event["title"]
        subtitle = event["sub_title"]

        data.append({
            "ticker": ticker, 
            "title": title,
            "sub_title": subtitle})

    return data

def main():
    client = get_client()
    response = get_events(client)
    data = parse_market_names(response)
    print(data)

if __name__ == "__main__":
    main()