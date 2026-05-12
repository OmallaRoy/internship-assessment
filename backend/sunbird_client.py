import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.sunbird.ai" # URL where all API requests are made to
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}
