"""
YouTube Authenticator Module

This module handles OAuth 2.0 authentication with the YouTube Data API v3.
It manages credential storage and refresh, providing a seamless authentication experience.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class YouTubeAuthenticator:
    """Handles OAuth 2.0 authentication flow for YouTube Data API v3."""
    
    # Define the required API scope
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    
    def __init__(self, client_secrets_file='client_secret.json', token_file='token.json'):
        """
        Initialize the authenticator with paths to credential files.
        
        Args:
            client_secrets_file (str): Path to the client secrets JSON file
            token_file (str): Path to store/retrieve the token
        """
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file

    def get_authenticated_service(self):
        """
        Authenticate and build the YouTube API service.
        
        Returns:
            googleapiclient.discovery.Resource: An authenticated YouTube API service object
        
        Raises:
            FileNotFoundError: If client_secret.json is not found
            Exception: For other authentication-related errors
        """
        credentials = None

        # Load existing credentials if they exist
        if os.path.exists(self.token_file):
            print("Loading existing credentials...")
            credentials = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        # If no valid credentials are available, refresh or get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("Refreshing expired credentials...")
                credentials.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets_file):
                    raise FileNotFoundError(
                        f"Client secrets file not found: {self.client_secrets_file}\n"
                        "Please obtain it from the Google Cloud Console and save it as "
                        "'client_secret.json' in the same directory."
                    )

                print("Starting new OAuth 2.0 authorization flow...")
                print("A browser window will open for authentication.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES
                )
                credentials = flow.run_local_server(port=8080)
                print("Authentication successful!")

            # Save the credentials for future runs
            print("Saving credentials for future use...")
            with open(self.token_file, 'w') as token:
                token.write(credentials.to_json())

        # Build and return the YouTube API service
        print("Building YouTube API service...")
        return build('youtube', 'v3', credentials=credentials)

if __name__ == '__main__':
    # Example usage
    try:
        authenticator = YouTubeAuthenticator()
        youtube = authenticator.get_authenticated_service()
        print("Successfully authenticated with YouTube API!")
        print("The YouTube service object is ready to use.")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
