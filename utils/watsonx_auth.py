"""
watsonx Orchestrate Authentication Manager
Handles IBM Cloud IAM token generation from API key
"""
import requests
from datetime import datetime, timedelta
from typing import Optional


class WatsonXAuthManager:
    """Manages IBM Cloud IAM token authentication"""

    def __init__(self, api_key: str):
        """
        Initialize authentication manager

        Args:
            api_key: IBM Cloud API key
        """
        self.api_key = api_key
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.iam_url = "https://iam.cloud.ibm.com/identity/token"

    def get_token(self) -> str:
        """
        Get valid IAM token (generates new if expired)

        Returns:
            Valid IAM access token
        """
        # Check if current token is still valid
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token

        # Generate new token
        return self._generate_token()

    def _generate_token(self) -> str:
        """
        Generate new IAM access token from API key

        Returns:
            Fresh IAM access token

        Raises:
            Exception: If token generation fails
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }

        try:
            response = requests.post(
                self.iam_url,
                headers=headers,
                data=data,
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self.token = token_data["access_token"]

            # IBM IAM tokens are valid for 60 minutes
            # Refresh at 55 minutes to avoid expiry during requests
            self.token_expiry = datetime.now() + timedelta(minutes=55)

            return self.token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate IAM token: {str(e)}")

    def get_headers(self) -> dict:
        """
        Get authorization headers with valid IAM token

        Returns:
            Dictionary with Authorization and Content-Type headers
        """
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def invalidate_token(self):
        """Force token refresh on next request"""
        self.token = None
        self.token_expiry = None
