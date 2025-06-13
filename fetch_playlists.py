from youtube_authenticator import YouTubeAuthenticator
import json
from pathlib import Path

def get_channel_id(youtube):
    """Get channel ID using a known video from the channel."""
    # Use a video ID we know is from the correct channel
    known_video_id = "--9G_GYL6ZY"  # This is from a retiro we downloaded
    
    try:
        # Get video details to find channel
        request = youtube.videos().list(
            part="snippet",
            id=known_video_id
        )
        response = request.execute()
        
        if response['items']:
            channel_id = response['items'][0]['snippet']['channelId']
            channel_title = response['items'][0]['snippet']['channelTitle']
            print(f"Found channel: {channel_title}")
            return channel_id
    except Exception as e:
        print(f"Error finding channel: {e}")
    
    return None
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['snippet']['channelId']
    return None

def fetch_channel_playlists(youtube):
    """Fetch all playlists from the channel."""
    channel_id = get_channel_id(youtube)
    if not channel_id:
        raise Exception("Channel not found")
        
    print(f"Found channel ID: {channel_id}")
    playlists = []
    next_page_token = None
    
    while True:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            channelId=channel_id,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for playlist in response['items']:
            playlist_data = {
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet']['description'],
                'publishedAt': playlist['snippet']['publishedAt'],
                'itemCount': playlist['contentDetails']['itemCount']
            }
            playlists.append(playlist_data)
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return playlists

def categorize_playlists(playlists):
    """Categorize playlists into Pujas, Retiros, and Others."""
    categorized = {
        'pujas': [],
        'retiros': [],
        'outros': []
    }
    
    retiro_keywords = ['retiro', 'retreat', 'séminaire', 'retraite']
    puja_keywords = ['puja', 'pujas']
    
    for playlist in playlists:
        title = playlist['title'].lower()
        is_retiro = any(keyword in title for keyword in retiro_keywords)
        is_puja = any(keyword in title for keyword in puja_keywords)
        
        if is_puja:
            categorized['pujas'].append(playlist)
        elif is_retiro:
            categorized['retiros'].append(playlist)
        else:
            categorized['outros'].append(playlist)
    
    return categorized

def main():
    # Initialize YouTube API
    auth = YouTubeAuthenticator()
    youtube = auth.get_youtube_service()
    
    # Fetch all playlists
    print("Buscando playlists do canal...")
    playlists = fetch_channel_playlists(youtube)
    
    # Categorize playlists
    categorized = categorize_playlists(playlists)
    
    # Save raw playlists data
    with open('playlists_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)
    
    # Save playlist IDs by category
    base_path = Path('playlists')
    base_path.mkdir(exist_ok=True)
    
    for category, items in categorized.items():
        filename = base_path / f'{category}_playlists.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            for playlist in items:
                f.write(f"{playlist['id']}\t{playlist['title']}\n")
    
    # Print summary
    print("\nResumo das Playlists encontradas:")
    print(f"Total de Playlists: {len(playlists)}")
    print(f"Pujas: {len(categorized['pujas'])}")
    print(f"Retiros: {len(categorized['retiros'])}")
    print(f"Outros: {len(categorized['outros'])}")
    
    print("\nArquivos criados:")
    print("- playlists_metadata.json (dados completos)")
    print("- playlists/pujas_playlists.txt")
    print("- playlists/retiros_playlists.txt")
    print("- playlists/outros_playlists.txt")

if __name__ == '__main__':
    main()
