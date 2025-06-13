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
        self._credentials = None
        
    def get_credentials(self):
        """
        Get valid credentials for YouTube API access.
        Handles token refresh and new authentication flow if necessary.
        
        Returns:
            google.oauth2.credentials.Credentials: Valid credentials for API access
        """
        if self._credentials and self._credentials.valid:
            return self._credentials
            
        # Check if we have stored token
        if os.path.exists(self.token_file):
            self._credentials = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
        # If credentials are expired but have refresh token, refresh them
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            self._credentials.refresh(Request())
            
        # If no valid credentials available, run the OAuth flow
        if not self._credentials or not self._credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.SCOPES)
            self._credentials = flow.run_local_server(port=0)
            
        # Save the credentials for future use
        with open(self.token_file, 'w') as token:
            token.write(self._credentials.to_json())
            
        return self._credentials
        
    def get_youtube_service(self):
        """
        Get an authenticated YouTube API service instance.
        
        Returns:
            googleapiclient.discovery.Resource: Authenticated YouTube API service
        """
        credentials = self.get_credentials()
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
