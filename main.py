#!/usr/bin/env python3
from youtube_authenticator import YouTubeAuthenticator
import json
from pathlib import Path
import time

def fetch_all_playlists(youtube):
    """Busca todas as playlists do canal e salva no arquivo de metadados"""
    print("Buscando playlists do canal...")
    
    channel_id = "UCz3WPsPTwekahMtKoz9YdmA"  # Canal Lama Padma Samten
    playlists = []
    next_page_token = None
    
    while True:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            playlist_info = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description']
            }
            playlists.append(playlist_info)
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        
        time.sleep(1)  # Evita exceder limites da API
    
    # Salva os metadados das playlists
    with open('playlists/playlists_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(playlists, f, indent=2, ensure_ascii=False)
    
    print(f"Total de playlists encontradas: {len(playlists)}")
    return playlists

def main():
    # 1. Autenticação
    print("Iniciando processo de autenticação...")
    authenticator = YouTubeAuthenticator()
    youtube = authenticator.get_youtube_service()
    
    if youtube:
        print("✅ Autenticação bem-sucedida!")
        print("🎵 Conectado à API do YouTube")
        
        # 2. Verifica se precisa atualizar metadados das playlists
        if not Path('playlists/playlists_metadata.json').exists():
            print("Arquivo de metadados não encontrado. Buscando playlists...")
            fetch_all_playlists(youtube)
        else:
            print("✅ Metadados das playlists já existem")
        
        print("\n🚀 Sistema pronto para uso!")
        print("Use: python3 main_playlist.py para gerenciar playlists")
    else:
        print("❌ Falha na autenticação")

if __name__ == "__main__":
    main()
