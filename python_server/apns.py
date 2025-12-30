import time
import jwt
import httpx
import logging
from .config import Config

logger = logging.getLogger("bark.apns")

class APNSClient:
    def __init__(self):
        self.client = httpx.AsyncClient(http2=True)
        self.token = None
        self.token_expiry = 0
    
    def get_jwt_token(self):
        """Generates a fresh JWT token for APNs if the current one is expired."""
        now = time.time()
        if self.token and now < self.token_expiry - 60: # Refresh 1 min before expiry
            return self.token

        try:
            with open(Config.APNS_KEY_PATH, 'r') as f:
                secret = f.read()

            algorithm = 'ES256'
            headers = {
                'alg': algorithm,
                'kid': Config.APNS_KEY_ID,
            }
            payload = {
                'iss': Config.APNS_TEAM_ID,
                'iat': int(now),
            }

            token = jwt.encode(payload, secret, algorithm=algorithm, headers=headers)
            
            self.token = token
            self.token_expiry = now + (60 * 50) # Valid for less than an hour (Apple limit is 1 hr)
            return token
        except Exception as e:
            logger.error(f"Failed to generate APNs token: {e}")
            raise e

    async def push(self, device_token: str, payload: dict):
        """Sends a push notification to APNs."""
        url = f"https://api.push.apple.com/3/device/{device_token}"
        
        headers = {
            "apns-topic": Config.APNS_TOPIC,
            "authorization": f"bearer {self.get_jwt_token()}",
            "apns-push-type": "alert"  # Required for iOS 13+
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return True, "Success"
            
            error_reason = response.json().get('reason', 'Unknown')
            logger.error(f"APNs Push Failed: {response.status_code} - {error_reason}")
            
            if response.status_code == 410: # Unregistered
                return False, "Unregistered"
            
            return False, error_reason
            
        except Exception as e:
            logger.error(f"APNs Request Error: {e}")
            return False, str(e)

apns_client = APNSClient()
