import random
import base64
import requests
from stringcolor import cs

def get_db():
    encoded = "aHR0cHM6Ly9wYWtzaW0uaW5mby9zaW0tZGF0YWJhc2Utb25saW5lLTIwMjItcmVzdWx0LnBocA=="
    return base64.b64decode(encoded).decode()

def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.257",
        "Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    ]
    ref_en = "aHR0cHM6Ly9wYWtzaW0uaW5mby9zZWFyY2gucGhw"
    ori_en = "aHR0cHM6Ly9wYWtzaW0uaW5mbw=="
    return {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': base64.b64decode(ref_en).decode(),
        'Origin': base64.b64decode(ori_en).decode(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cache-Control': 'max-age=0'
    }

def fetch_data(value):
    db_url = get_db()
    headers = get_headers()
    try:
        response = requests.post(db_url, data={"cnnum": value}, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception:
        print(cs("\n[!] Connection Error: Please check your internet connection or try again later.\n", "red").bold())
        return None

headers = get_headers()