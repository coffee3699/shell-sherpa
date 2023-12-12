import requests
import os
import dotenv

# Load environment variables
dirname = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(dirname, ".env"))
api_key = os.getenv("API_KEY")

# Proxy API URL and headers
API_URL = "https://api.pawan.krd/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json"
}


def ask(message, system="", model="pai-001-light-beta"):
    data = {
        "model": model,
        "max_tokens": 500,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    # Send POST request to the proxy API
    response = requests.post(API_URL, headers=HEADERS, json=data)

    # Handle the response
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
