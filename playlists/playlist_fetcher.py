"""
Playlist Fetcher Module

This module fetches all video IDs from specified YouTube playlists,
handling pagination and ensuring unique video IDs are collected.
"""

from typing import List, Set
import os
from youtube_authenticator import YouTubeAuthenticator

class PlaylistFetcher:
    """Handles fetching video IDs from YouTube playlists."""
    
    # Replace these with your actual playlist IDs
    PLAYLIST_IDS = [
        'PLxxxxxxxxxxxx1',  # Replace with your actual playlist IDs
        'PLxxxxxxxxxxxx2'
    ]
    
    def __init__(self, output_file: str = 'video_ids.txt'):
        """
        Initialize the PlaylistFetcher.
        
        Args:
            output_file (str): Path to the output file for video IDs
        """
        self.output_file = output_file
        self.authenticator = YouTubeAuthenticator()
        self.youtube = self.authenticator.get_authenticated_service()
        
    def fetch_playlist_items(self, playlist_id: str) -> List[str]:
        """
        Fetch all video IDs from a single playlist, handling pagination.
        
        Args:
            playlist_id (str): The ID of the YouTube playlist
            
        Returns:
            List[str]: List of video IDs from the playlist
        """
        video_ids = []
        next_page_token = None
        
        while True:
            try:
                # Make the API request
                request = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,  # Maximum allowed by the API
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Extract video IDs from the response
                for item in response.get('items', []):
                    video_id = item['contentDetails']['videoId']
                    video_ids.append(video_id)
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except Exception as e:
                print(f"Error fetching playlist {playlist_id}: {str(e)}")
                break
        
        return video_ids
    
    def fetch_all_playlists(self) -> Set[str]:
        """
        Fetch video IDs from all configured playlists.
        
        Returns:
            Set[str]: Set of unique video IDs from all playlists
        """
        all_video_ids = set()  # Using a set to automatically handle duplicates
        
        for playlist_id in self.PLAYLIST_IDS:
            print(f"Fetching videos from playlist: {playlist_id}")
            video_ids = self.fetch_playlist_items(playlist_id)
            all_video_ids.update(video_ids)
            print(f"Found {len(video_ids)} videos in playlist {playlist_id}")
        
        return all_video_ids
    
    def save_video_ids(self, video_ids: Set[str]):
        """
        Save the unique video IDs to a text file.
        
        Args:
            video_ids (Set[str]): Set of unique video IDs to save
        """
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for video_id in sorted(video_ids):  # Sorting for consistency
                f.write(f"{video_id}\n")
    
    def process(self):
        """
        Main process to fetch all video IDs and save them to a file.
        """
        print("Starting to fetch video IDs from all playlists...")
        video_ids = self.fetch_all_playlists()
        print(f"\nTotal unique videos found: {len(video_ids)}")
        
        print(f"\nSaving video IDs to {self.output_file}...")
        self.save_video_ids(video_ids)
        print("Done!")

if __name__ == '__main__':
    try:
        fetcher = PlaylistFetcher()
        fetcher.process()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
