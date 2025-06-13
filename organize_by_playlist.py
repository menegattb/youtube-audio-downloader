import json
import os
import shutil
from pathlib import Path

def sanitize_folder_name(name):
    """Remove caracteres inválidos do nome da pasta"""
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, '-')
    return name

def get_video_id_from_filename(filename):
    """Extrai o ID do vídeo do nome do arquivo usando o video_metadata.json"""
    # Carregar metadados dos vídeos
    with open('video_metadata.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    # Criar mapeamento título -> id
    title_to_id = {video['title']: video['video_id'] for video in videos}
    
    # Remover extensão .mp3
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Procurar pelo título nos metadados
    for title, video_id in title_to_id.items():
        if name_without_ext == title:
            return video_id
            
    return None

def get_playlist_videos():
    """Obter mapeamento de playlist -> vídeos usando a API do YouTube"""
    from youtube_authenticator import YouTubeAuthenticator
    
    auth = YouTubeAuthenticator()
    youtube = auth.get_youtube_service()
    
    playlist_videos = {}
    
    with open('playlists_metadata.json', 'r', encoding='utf-8') as f:
        playlists = json.load(f)
    
    for playlist in playlists:
        playlist_id = playlist['id']
        videos = []
        next_page_token = None
        
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            try:
                response = request.execute()
                for item in response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    videos.append(video_id)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            except Exception as e:
                print(f"Erro ao buscar vídeos da playlist {playlist_id}: {e}")
                break
        
        playlist_videos[playlist_id] = videos
    
    return playlist_videos

def organize_files():
    # Carregar metadados das playlists
    with open('playlists_metadata.json', 'r', encoding='utf-8') as f:
        playlists = json.load(f)
    
    # Obter mapeamento de playlist -> vídeos
    playlist_videos = get_playlist_videos()
    
    # Criar dicionário de playlist_id -> título
    playlist_info = {p['id']: {'title': p['title'], 'videos': playlist_videos.get(p['id'], [])} 
                    for p in playlists}
    
    # Base path para os arquivos de áudio
    base_path = Path('/Users/bno/Documents/PyAPIyt/downloads/audio')
    playlists_path = base_path / 'playlists'
    playlists_path.mkdir(exist_ok=True)
    
    # Lista todos os arquivos MP3
    mp3_files = list(base_path.glob('*.mp3'))
    
    # Para cada arquivo, verificar em quais playlists ele pertence
    videos_moved = set()
    for file in mp3_files:
        video_id = get_video_id_from_filename(file.name)
        if not video_id:
            continue
            
        # Verificar em quais playlists este vídeo aparece
        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_title = sanitize_folder_name(playlist['title'])
            
            # Criar pasta da playlist se necessário
            playlist_folder = playlists_path / playlist_title
            playlist_folder.mkdir(exist_ok=True)
            
            # Se o vídeo pertence a esta playlist, copiar para a pasta
            target_path = playlist_folder / file.name
            if not target_path.exists():
                shutil.copy2(file, target_path)
                print(f"Copiado: {file.name} -> {playlist_title}")
                videos_moved.add(video_id)

    # Criar relatório
    print("\nRelatório:")
    print(f"Total de arquivos processados: {len(mp3_files)}")
    print(f"Vídeos movidos para playlists: {len(videos_moved)}")

if __name__ == '__main__':
    organize_files()
