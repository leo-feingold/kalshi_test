import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

from clients import KalshiHttpClient, Environment

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

# Run a test: Get your account balance
balance = client.get_balance()
print("Your balance:", balance)
