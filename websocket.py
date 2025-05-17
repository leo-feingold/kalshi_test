import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
import asyncio
import ssl
import certifi


ssl._create_default_https_context = ssl.create_default_context
ssl.create_default_context = lambda *args, **kwargs: ssl._create_default_https_context(cafile=certifi.where())


from clients import KalshiHttpClient, KalshiWebSocketClient, Environment

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

# Initialize the WebSocket client
ws_client = KalshiWebSocketClient(
    key_id=KEYID,
    private_key=private_key,
    environment=env
)

# Connect via WebSocket
asyncio.run(ws_client.connect())
