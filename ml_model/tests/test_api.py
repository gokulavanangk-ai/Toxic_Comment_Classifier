import requests
import time
import sys

def test_api():
    url = "http://127.0.0.1:8000/predict"
    data = {"text": "ne sethudu"}
    
    print(f"Testing API at {url} with data: {data}")
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed with status {response.status_code}")
            print(response.text)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
