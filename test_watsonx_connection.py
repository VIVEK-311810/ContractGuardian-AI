"""
Quick test script to verify watsonx Orchestrate connection
"""
from utils.watsonx_auth import WatsonXAuthManager
from config.settings import WATSONX_API_KEY, WATSONX_INSTANCE_URL, AGENT_IDS
import requests


def test_authentication():
    """Test IAM token generation"""
    print("=" * 60)
    print("Testing IAM Authentication...")
    print("=" * 60)

    try:
        auth_manager = WatsonXAuthManager(WATSONX_API_KEY)
        token = auth_manager.get_token()
        print(f"[OK] Token generated successfully")
        print(f"   Token preview: {token[:50]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Authentication failed: {e}")
        return False


def test_agent_endpoint():
    """Test agent endpoint connectivity"""
    print("\n" + "=" * 60)
    print("Testing Agent Endpoint...")
    print("=" * 60)

    try:
        auth_manager = WatsonXAuthManager(WATSONX_API_KEY)
        agent_id = AGENT_IDS['ingestion']['agent_id']

        endpoint = f"{WATSONX_INSTANCE_URL}/v1/orchestrate/{agent_id}/chat/completions"
        print(f"   Endpoint: {endpoint}")

        payload = {
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "stream": False
        }

        response = requests.post(
            endpoint,
            headers=auth_manager.get_headers(),
            json=payload,
            timeout=30
        )

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"[OK] Agent responded successfully")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print(f"[FAIL] Agent returned error: {response.text}")
            return False

    except Exception as e:
        print(f"[FAIL] Agent test failed: {e}")
        return False


def test_configuration():
    """Test configuration values"""
    print("\n" + "=" * 60)
    print("Testing Configuration...")
    print("=" * 60)

    print(f"   Instance URL: {WATSONX_INSTANCE_URL}")
    print(f"   API Key: {WATSONX_API_KEY[:20]}...{WATSONX_API_KEY[-10:]}")
    print(f"\n   Agent IDs:")
    for key, config in AGENT_IDS.items():
        print(f"   - {key}: {config['agent_id']}")

    # Validate all configs exist
    if all([WATSONX_INSTANCE_URL, WATSONX_API_KEY]):
        if all([cfg['agent_id'] for cfg in AGENT_IDS.values()]):
            print(f"\n[OK] All configuration values present")
            return True

    print(f"\n[FAIL] Missing configuration values")
    return False


def main():
    """Run all tests"""
    print("\n")
    print("watsonx Orchestrate Connection Test")
    print("=" * 60)

    results = {
        "Configuration": test_configuration(),
        "Authentication": test_authentication(),
        "Agent Endpoint": test_agent_endpoint()
    }

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"   {test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: All tests passed! watsonx integration is ready.")
    else:
        print("WARNING: Some tests failed. Please check configuration and connectivity.")
    print("=" * 60 + "\n")

    return all_passed


if __name__ == "__main__":
    main()
