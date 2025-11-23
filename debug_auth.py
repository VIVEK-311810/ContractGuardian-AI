"""Debug authentication to see what's wrong"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WATSONX_API_KEY")

print(f"API Key loaded: {api_key}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:15] if api_key else 'None'}")

# Try authentication
url = "https://iam.cloud.ibm.com/identity/token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key
}

print(f"\nSending request to: {url}")
print(f"Grant type: {data['grant_type']}")
print(f"API Key (redacted): {api_key[:20]}...{api_key[-10:]}")

try:
    response = requests.post(url, headers=headers, data=data, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200:
        token_data = response.json()
        print(f"\n[SUCCESS] Token generated!")
        print(f"Token type: {token_data.get('token_type')}")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
    else:
        print(f"\n[ERROR] Authentication failed")
        print(f"Response body: {response.text}")

except Exception as e:
    print(f"\n[EXCEPTION] {e}")
