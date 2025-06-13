#!/usr/bin/env python3
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from youtube_authenticator import YouTubeAuthenticator
import json
import os
import subprocess
import time
from datetime import datetime

def sanitize_folder_name(name):
    """Remove caracteres inválidos do nome da pasta"""
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, '-')
    return name

def prepare_playlist_structure(playlist_id):
    """
    Prepara a estrutura de pastas para uma playlist específica.
    Retorna o caminho da pasta criada e o título da playlist.
    """
    # Carregar metadados das playlists
    metadata_path = Path(__file__).parent / 'playlists_metadata.json'
    with open(metadata_path, 'r', encoding='utf-8') as f:
        playlists = json.load(f)
    
    # Encontrar a playlist específica
    playlist_info = None
    for p in playlists:
        if p['id'] == playlist_id:
            playlist_info = p
            break
    
    if not playlist_info:
        raise ValueError(f"Playlist {playlist_id} não encontrada nos metadados")
    
    # Criar estrutura de pastas
    base_path = root_dir / 'downloads/audio'
    playlist_folder = sanitize_folder_name(playlist_info['title'])
    playlist_path = base_path / playlist_folder
    
    # Criar pasta se não existir
    playlist_path.mkdir(exist_ok=True, parents=True)
    
    print(f"Estrutura preparada para playlist: {playlist_info['title']}")
    print(f"Pasta criada em: {playlist_path}")
    
    return playlist_path, playlist_info['title']

class PlaylistDownloader:
    def __init__(self):
        self.youtube = YouTubeAuthenticator().get_youtube_service()
        self.progress_file = root_dir / 'downloads/audio/playlist_progress.json'
        self.load_progress()

    def load_progress(self):
        """Carrega ou cria o arquivo de progresso das playlists"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'playlists': {},
                'last_update': datetime.now().isoformat()
            }
            self.save_progress()

    def save_progress(self):
        """Salva o progresso atual no arquivo"""
        self.progress['last_update'] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def get_playlist_videos(self, playlist_id):
        """Obtém todos os vídeos de uma playlist"""
        videos = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                title = item['snippet']['title']
                position = item['snippet']['position']
                videos.append({
                    'video_id': video_id,
                    'title': title,
                    'position': position
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return sorted(videos, key=lambda x: x['position'])

    def display_progress(self, playlist_id, current, total):
        """Exibe o progresso do download da playlist"""
        progress = self.progress['playlists'][playlist_id]
        percentage = (current / total) * 100
        print(f"\nProgresso da Playlist: {progress['title']}")
        print(f"Vídeos baixados: {current}/{total} ({percentage:.1f}%)")
        print("=" * 50)

    def download_video(self, video, playlist_id, position, total_videos):
        """Baixa um vídeo específico"""
        # Prepara a estrutura de pastas e obtém o caminho
        playlist_path, _ = prepare_playlist_structure(playlist_id)
        
        # Format the position number with leading zeros based on total videos
        position_str = str(position + 1).zfill(len(str(total_videos)))
        output_template = str(playlist_path / f"{position_str} - %(title)s.%(ext)s")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                cmd = [
                    "yt-dlp",
                    "--cookies", "cookies.txt",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--no-overwrites",
                    "-o", output_template,
                    f"https://www.youtube.com/watch?v={video['video_id']}"
                ]
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return True
            except subprocess.CalledProcessError as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Tentativa {retry_count} falhou. Tentando novamente em 5 segundos...")
                    time.sleep(5)
                else:
                    print(f"Erro ao baixar {video['title']} após {max_retries} tentativas: {e.stderr}")
                    return False
        
        return False

    def download_playlist(self, playlist_id, playlist_title):
        """Baixa todos os vídeos de uma playlist, mantendo o progresso"""
        print(f"\nIniciando download da playlist: {playlist_title}")
        
        # Inicializa o progresso desta playlist se não existir
        if playlist_id not in self.progress['playlists']:
            self.progress['playlists'][playlist_id] = {
                'title': playlist_title,
                'downloaded_videos': [],
                'status': 'in_progress',
                'last_position': -1,
                'total_videos': 0,
                'completed_videos': 0
            }
            self.save_progress()
        
        # Obtém os vídeos da playlist
        videos = self.get_playlist_videos(playlist_id)
        total_videos = len(videos)
        
        # Atualiza o total de vídeos no progresso
        self.progress['playlists'][playlist_id]['total_videos'] = total_videos
        self.save_progress()
        
        # Retoma do último vídeo baixado
        start_pos = self.progress['playlists'][playlist_id]['last_position'] + 1
        
        # Exibe progresso inicial
        self.display_progress(playlist_id, len(self.progress['playlists'][playlist_id]['downloaded_videos']), total_videos)
        
        for i, video in enumerate(videos[start_pos:], start=start_pos):
            if video['video_id'] in self.progress['playlists'][playlist_id]['downloaded_videos']:
                print(f"Vídeo {i+1}/{total_videos} já baixado, pulando...")
                continue
            
            print(f"\nBaixando {i+1}/{total_videos}: {video['title']}")
            if self.download_video(video, playlist_id, i, total_videos):
                self.progress['playlists'][playlist_id]['downloaded_videos'].append(video['video_id'])
                self.progress['playlists'][playlist_id]['last_position'] = i
                self.progress['playlists'][playlist_id]['completed_videos'] = len(self.progress['playlists'][playlist_id]['downloaded_videos'])
                self.save_progress()
                print(f"Download concluído ({i+1}/{total_videos}): {video['title']}")
                self.display_progress(playlist_id, len(self.progress['playlists'][playlist_id]['downloaded_videos']), total_videos)
                time.sleep(2)  # Pequena pausa entre downloads
            else:
                print(f"Falha no download de {video['title']}, tentando próximo...")
        
        # Marca playlist como concluída
        if len(self.progress['playlists'][playlist_id]['downloaded_videos']) == total_videos:
            self.progress['playlists'][playlist_id]['status'] = 'completed'
            self.save_progress()
            print(f"\nPlaylist {playlist_title} concluída!")

    def download_all_playlists(self):
        """Baixa todas as playlists do arquivo de metadados"""
        metadata_path = Path(__file__).parent / 'playlists_metadata.json'
        with open(metadata_path, 'r', encoding='utf-8') as f:
            playlists = json.load(f)
        
        total_playlists = len(playlists)
        completed = 0
        
        for playlist in playlists:
            completed += 1
            playlist_id = playlist['id']
            title = playlist['title']
            
            print(f"\n=== Playlist {completed}/{total_playlists} ===")
            
            if playlist_id in self.progress['playlists']:
                if self.progress['playlists'][playlist_id]['status'] == 'completed':
                    print(f"Playlist já concluída: {title}")
                    continue
            
            self.download_playlist(playlist_id, title)

def main():
    downloader = PlaylistDownloader()
    downloader.download_all_playlists()

if __name__ == '__main__':
    main()
