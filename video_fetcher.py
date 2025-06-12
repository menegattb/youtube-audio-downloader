"""
YouTube Video and Playlist Fetcher

This module fetches all video IDs from:
1. All playlists in your YouTube account
2. All individual videos in your YouTube account
"""

import os
from typing import List, Set
from youtube_authenticator import YouTubeAuthenticator
from googleapiclient.errors import HttpError

class VideoFetcher:
    def __init__(self):
        """Initialize the VideoFetcher with authenticated YouTube service."""
        self.authenticator = YouTubeAuthenticator()
        self.youtube = self.authenticator.get_authenticated_service()
        self.all_video_ids: Set[str] = set()

    def fetch_playlist_ids(self) -> List[str]:
        """Fetch all playlist IDs from the user's YouTube account."""
        print("\nFetching your playlists...")
        playlist_ids = []
        next_page_token = None
        
        while True:
            playlists_request = self.youtube.playlists().list(
                part="id,snippet",
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )
            
            try:
                playlists_response = playlists_request.execute()
                for playlist in playlists_response.get("items", []):
                    playlist_id = playlist["id"]
                    title = playlist["snippet"]["title"]
                    print(f"Found playlist: {title}")
                    playlist_ids.append(playlist_id)
                
                next_page_token = playlists_response.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Error fetching playlists: {str(e)}")
                break
                
        print(f"Total playlists found: {len(playlist_ids)}")
        return playlist_ids

    def fetch_videos_from_playlist(self, playlist_id: str):
        """Fetch all video IDs from a specific playlist."""
        next_page_token = None
        
        while True:
            playlist_items_request = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            
            try:
                playlist_items = playlist_items_request.execute()
                for item in playlist_items.get("items", []):
                    video_id = item["contentDetails"]["videoId"]
                    self.all_video_ids.add(video_id)
                
                next_page_token = playlist_items.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Error fetching videos from playlist {playlist_id}: {str(e)}")
                break

    def fetch_channel_videos(self):
        """Fetch all videos from the user's channel that aren't in playlists."""
        print("\nFetching your individual videos...")
        next_page_token = None
        
        while True:
            videos_request = self.youtube.search().list(
                part="id",
                forMine=True,
                type="video",
                maxResults=50,
                pageToken=next_page_token
            )
            
            try:
                videos_response = videos_request.execute()
                for item in videos_response.get("items", []):
                    video_id = item["id"]["videoId"]
                    self.all_video_ids.add(video_id)
                
                next_page_token = videos_response.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Error fetching channel videos: {str(e)}")
                break

    def save_video_ids(self):
        """Save all collected video IDs to a file."""
        sorted_video_ids = sorted(list(self.all_video_ids))
        
        with open("video_ids.txt", "w") as f:
            for video_id in sorted_video_ids:
                f.write(f"https://www.youtube.com/watch?v={video_id}\n")
                
        print(f"\nSaved {len(sorted_video_ids)} unique video URLs to video_ids.txt")

    def fetch_all_videos(self):
        """Main method to fetch all videos from playlists and channel."""
        print("Starting to fetch all your YouTube videos...")
        
        # First, get all playlists
        playlist_ids = self.fetch_playlist_ids()
        
        # Then fetch videos from each playlist
        print("\nFetching videos from playlists...")
        for i, playlist_id in enumerate(playlist_ids, 1):
            print(f"Processing playlist {i} of {len(playlist_ids)}...")
            self.fetch_videos_from_playlist(playlist_id)
            
        # Finally, fetch videos that aren't in playlists
        self.fetch_channel_videos()
        
        # Save all video IDs
        self.save_video_ids()

if __name__ == "__main__":
    try:
        print("Iniciando o processo...")
        fetcher = VideoFetcher()
        print("VideoFetcher criado com sucesso!")
        fetcher.fetch_all_videos()
        print("\nProcess completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
