import requests
import json
from time import sleep

BASE_URL = "http://kahn:5000"

# Test for generating an API key
def test_generate_api_key():
    print("Testing API key generation...")
    response = requests.get(f"{BASE_URL}/getkey")
    if response.status_code == 200:
        print("API key generated successfully.")
        api_key = response.json().get('api_key')
        expires_in = response.json().get('expires_in')
        print(f"API Key: {api_key}, Expires in: {expires_in} seconds")
        return api_key
    else:
        print(f"Failed to generate API key. Status code: {response.status_code}")
        print(response.json())
        return None

# Test for validating an API key
def test_validate_api_key(api_key):
    print(f"Testing API key validation for key: {api_key}...")
    response = requests.get(f"{BASE_URL}/validatekey/{api_key}")
    if response.status_code == 200:
        print("API key is valid.")
        print(response.json())
    else:
        print(f"Failed to validate API key. Status code: {response.status_code}")
        print(response.json())

# Test for storing data in MongoDB
def test_store_data(api_key):
    print(f"Testing storing data with API key: {api_key}...")
    data = {
        "name": "Test",
        "value": 123
    }
    headers = {"X-API-KEY": api_key}
    response = requests.post(f"{BASE_URL}/insert", json=data, headers=headers)
    if response.status_code == 200:
        print("Data stored successfully.")
        print(response.json())
    else:
        print(f"Failed to store data. Status code: {response.status_code}")
        print(response.json())

# Test for querying values from MongoDB
def test_query_field():
    print("Testing querying field from MongoDB...")
    response = requests.get(f"{BASE_URL}/getvalues", params={"field": "name"})
    if response.status_code == 200:
        print("Query successful.")
        print(response.json())
    else:
        print(f"Failed to query values. Status code: {response.status_code}")
        print(response.json())

# Main testing function
def main():
    # Step 1: Generate API Key
    api_key = test_generate_api_key()
    if not api_key:
        print("Skipping the rest of the tests due to failed API key generation.")
        return
    
    # Step 2: Validate the generated API key
    test_validate_api_key(api_key)

    # Step 3: Store data in MongoDB
    test_store_data(api_key)

    # Step 4: Query field values from MongoDB
    test_query_field()

if __name__ == "__main__":
    main()
