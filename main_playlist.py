#!/usr/bin/env python3
from playlists.playlist_downloader import PlaylistDownloader
from youtube_authenticator import YouTubeAuthenticator
import json
from pathlib import Path
import time

def fetch_all_playlists(youtube):
    """Busca todas as playlists do canal e salva no arquivo de metadados"""
    print("Buscando playlists do canal...")
    
    channel_id = "UCY2cdE2CjQEZGpC7ErNBjqQ"  # Canal Lama Padma Samten
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
    
    # Salva os metadados das playlists e atualiza o arquivo de playlists
    metadata_path = Path('playlists/playlists_metadata.json')
    playlists_path = Path('playlists/playlists.txt')
    metadata_path.parent.mkdir(exist_ok=True)
    
    # Salva os metadados em JSON
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(playlists, f, indent=2, ensure_ascii=False)
    
    # Atualiza o arquivo de playlists em formato de texto
    with open(playlists_path, 'w', encoding='utf-8') as f:
        for playlist in playlists:
            f.write(f"{playlist['id']}|{playlist['title']}\n")
    
    print(f"Total de playlists encontradas: {len(playlists)}")
    return playlists

def check_playlists_status(playlists, downloader):
    """Verifica o status de todas as playlists e mostra um relatório"""
    print("\nRelatório de Status das Playlists:")
    print("=" * 50)
    
    total = len(playlists)
    completed = 0
    in_progress = 0
    not_started = 0
    failed = []
    
    for playlist in playlists:
        playlist_id = playlist['id']
        if playlist_id in downloader.progress['playlists']:
            progress = downloader.progress['playlists'][playlist_id]
            if progress['status'] == 'completed':
                completed += 1
            else:
                in_progress += 1
                if progress.get('total_videos', 0) > 0:
                    completed_videos = len(progress['downloaded_videos'])
                    total_videos = progress['total_videos']
                    if completed_videos < total_videos:
                        failed.append({
                            'title': playlist['title'],
                            'completed': completed_videos,
                            'total': total_videos,
                            'id': playlist_id
                        })
        else:
            not_started += 1
    
    print(f"Total de Playlists: {total}")
    print(f"Concluídas: {completed}")
    print(f"Em Progresso: {in_progress}")
    print(f"Não Iniciadas: {not_started}")
    
    if failed:
        print("\nPlaylists com downloads incompletos:")
        for f in failed:
            print(f"- {f['title']}")
            print(f"  Progresso: {f['completed']}/{f['total']} vídeos")
    
    return failed

def main():
    # 1. Autenticação
    print("Iniciando processo de gerenciamento de playlists...")
    authenticator = YouTubeAuthenticator()
    youtube = authenticator.get_youtube_service()
    
    # 2. Verifica se precisa atualizar metadados das playlists
    metadata_path = Path('playlists/playlists_metadata.json')
    if not metadata_path.exists():
        print("Arquivo de metadados não encontrado. Buscando playlists...")
        playlists = fetch_all_playlists(youtube)
    else:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            playlists = json.load(f)
        print(f"Total de playlists carregadas: {len(playlists)}")
    
    # 3. Opções do usuário
    downloader = PlaylistDownloader()
    
    # Mostra status inicial
    failed_playlists = check_playlists_status(playlists, downloader)

    while True:
        print("\nGerenciamento de Playlists")
        print("1. Atualizar lista de playlists")
        print("2. Listar todas as playlists")
        print("3. Buscar playlist por nome")
        print("4. Baixar uma playlist específica")
        print("5. Baixar todas as playlists")
        print("6. Baixar várias playlists da lista")
        print("7. Retomar downloads incompletos")
        print("8. Verificar status das playlists")
        print("9. Sair")
        
        choice = input("\nEscolha uma opção (1-9): ")
        
        if choice == "1":
            playlists = fetch_all_playlists(youtube)
        elif choice == "2":
            print("\nLista de todas as playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"{i}. {playlist['title']}")
        elif choice == "3":
            search = input("\nDigite o termo de busca: ").lower()
            found = False
            for playlist in playlists:
                if search in playlist['title'].lower():
                    print(f"\nID: {playlist['id']}")
                    print(f"Título: {playlist['title']}")
                    print(f"Descrição: {playlist['description']}")
                    found = True
            if not found:
                print("Nenhuma playlist encontrada com esse termo.")
        elif choice == "4":
            search = input("\nDigite o termo para buscar a playlist desejada: ").lower()
            matching_playlists = []
            for i, playlist in enumerate(playlists):
                if search in playlist['title'].lower():
                    matching_playlists.append((i+1, playlist))
            
            if not matching_playlists:
                print("Nenhuma playlist encontrada com esse termo.")
                continue
            
            print("\nPlaylists encontradas:")
            for num, playlist in matching_playlists:
                print(f"{num}. {playlist['title']}")
            
            try:
                selection = int(input("\nDigite o número da playlist para baixar (0 para cancelar): "))
                if selection == 0:
                    continue
                
                for num, playlist in matching_playlists:
                    if num == selection:
                        print(f"\nIniciando download da playlist: {playlist['title']}")
                        downloader.download_playlist(playlist['id'], playlist['title'])
                        break
            except ValueError:
                print("Por favor, digite um número válido.")
        elif choice == "5":
            print("\nIniciando download de todas as playlists...")
            downloader.download_all_playlists()
        elif choice == "6":
            print("\nLista de todas as playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"{i}. {playlist['title']}")
            
            try:
                selections = input("\nDigite os números das playlists para baixar (separados por espaço): ").split()
                selections = [int(s) for s in selections if s.isdigit() and 1 <= int(s) <= len(playlists)]
                
                if not selections:
                    print("Nenhum número válido fornecido.")
                    continue
                
                print(f"\nBaixando {len(selections)} playlists:")
                for num in selections:
                    playlist = playlists[num-1]
                    print(f"\nIniciando download da playlist: {playlist['title']}")
                    downloader.download_playlist(playlist['id'], playlist['title'])
                    
            except ValueError:
                print("Por favor, digite números válidos separados por espaço.")
        elif choice == "7":
            print("\nRetomando downloads incompletos...")
            for playlist in failed_playlists:
                print(f"\nIniciando download da playlist: {playlist['title']}")
                downloader.download_playlist(playlist['id'], playlist['title'])
            
            # Atualiza o status após retomar downloads
            failed_playlists = check_playlists_status(playlists, downloader)
        elif choice == "8":
            # Verifica o status das playlists
            print("\nVerificando status das playlists...")
            failed_playlists = check_playlists_status(playlists, downloader)
        elif choice == "9":
            print("Encerrando...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
