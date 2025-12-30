import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_push():
    # Get configuration
    server_url = os.getenv("BARK_SERVER_URL", "http://localhost:8080")
    device_key = os.getenv("BARK_DEVICE_KEY")

    if not device_key:
        print("Error: BARK_DEVICE_KEY not found in .env file.")
        print("Please add it: BARK_DEVICE_KEY=your_key_here")
        return

    # Get message from arguments or use default
    if len(sys.argv) > 1:
        content = " ".join(sys.argv[1:])
    else:
        content = "Test Notification from Script"

    # Construct URL
    url = f"{server_url}/{device_key}/{content}"

    try:
        response = requests.get(url)
        print(f"Sending to: {url}")
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    send_push()
