"""
Test generating a real IAM token from the API key
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("WATSONX_API_KEY")

print(f"Testing IAM token generation...")
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

# Generate IAM token
url = "https://iam.cloud.ibm.com/identity/token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key
}

try:
    print("Requesting IAM token from IBM Cloud...")
    response = requests.post(url, headers=headers, data=data, timeout=30)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]

        print("[SUCCESS] IAM token generated!")
        print(f"Token type: {token_data.get('token_type')}")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
        print(f"Token preview: {access_token[:50]}...")
        print()

        # Now test with the real IAM token
        print("Testing agent endpoint with IAM token...")

        agent_id = "6924a712-d770-4f32-8878-396497b35181"
        instance_url = os.getenv("WATSONX_INSTANCE_URL")
        endpoint = f"{instance_url}/v1/orchestrate/{agent_id}/chat/completions"

        agent_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "messages": [
                {"role": "user", "content": "Hello, test message."}
            ],
            "stream": False
        }

        agent_response = requests.post(endpoint, headers=agent_headers, json=payload, timeout=30)

        print(f"Agent Status Code: {agent_response.status_code}")

        if agent_response.status_code == 200:
            print("[SUCCESS] Agent responded!")
            data = agent_response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"Response: {content[:200]}...")
        else:
            print(f"[FAIL] Agent error: {agent_response.text}")

    else:
        print(f"[FAIL] Could not generate IAM token")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[ERROR] {e}")
