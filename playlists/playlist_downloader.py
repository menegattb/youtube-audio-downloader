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
        self.error_log_file = root_dir / 'downloads/audio/download_errors.log'
        self.load_progress()

    def log_error(self, playlist_id, video_id, error_msg):
        """Registra erros de download em um arquivo de log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_entry = f"[{timestamp}] Playlist: {playlist_id}, Video: {video_id}\n{error_msg}\n{'='*50}\n"
        
        with open(self.error_log_file, 'a', encoding='utf-8') as f:
            f.write(error_entry)

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
        failed_count = len(progress.get('failed_videos', []))
        
        print(f"\nProgresso da Playlist: {progress['title']}")
        print(f"Vídeos baixados: {current}/{total} ({percentage:.1f}%)")
        if failed_count > 0:
            print(f"Vídeos com falha: {failed_count}")
        print("=" * 50)

    def check_download_status(self, output_template, video_id):
        """Verifica se o download foi realmente concluído verificando o arquivo"""
        # Espera um momento para o sistema de arquivos atualizar
        time.sleep(1)
        
        # Verifica se algum arquivo foi criado com o padrão correto
        output_dir = Path(output_template).parent
        expected_pattern = Path(output_template).name.replace('%(title)s', '*').replace('%(ext)s', 'mp3')
        matching_files = list(output_dir.glob(expected_pattern))
        
        if not matching_files:
            return False, "Arquivo não encontrado após download"
        
        # Verifica o tamanho do arquivo (deve ser maior que 1KB)
        file_size = matching_files[0].stat().st_size
        if file_size < 1024:
            return False, f"Arquivo muito pequeno ({file_size} bytes)"
            
        return True, None

    def download_video(self, video, playlist_id, position, total_videos):
        """Baixa um vídeo específico"""
        # Prepara a estrutura de pastas e obtém o caminho
        playlist_path, _ = prepare_playlist_structure(playlist_id)
        
        # Format the position number with leading zeros based on total videos
        position_str = str(position + 1).zfill(len(str(total_videos)))
        output_template = str(playlist_path / f"{position_str} - %(title)s.%(ext)s")
        
        max_retries = 5
        retry_count = 0
        retry_delay = 10
        
        while retry_count < max_retries:
            try:
                cmd = [
                    "yt-dlp",
                    "--cookies", str(root_dir / "cookies.txt"),
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--no-overwrites",
                    "--limit-rate", "1M",
                    "--sleep-interval", "3",
                    "--max-sleep-interval", "6",
                    "--retries", "3",
                    "--fragment-retries", "10",
                    "--force-ipv4",
                    "--no-check-certificate",  # Ignora problemas de certificado
                    "--no-warnings",  # Reduz ruído na saída
                    "--no-progress",  # Evita poluir o log com barras de progresso
                    "-o", output_template,
                    f"https://www.youtube.com/watch?v={video['video_id']}"
                ]
                
                print(f"Iniciando download de: {video['title']}")
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                
                # Verifica se o download foi realmente bem sucedido
                success, error_msg = self.check_download_status(output_template, video['video_id'])
                if not success:
                    raise Exception(f"Falha na verificação do download: {error_msg}")
                
                return True
                
            except subprocess.CalledProcessError as e:
                retry_count += 1
                error_msg = e.stderr.strip()
                self.log_error(playlist_id, video['video_id'], 
                             f"Erro de processo (tentativa {retry_count}):\n{error_msg}")
                
                if "Video unavailable" in error_msg:
                    print(f"Vídeo indisponível: {video['title']}")
                    return False
                
                if retry_count < max_retries:
                    wait_time = retry_delay * (2 ** (retry_count - 1))
                    print(f"Tentativa {retry_count} falhou. Aguardando {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    print(f"Todas as tentativas falharam para: {video['title']}")
                    return False
                    
            except Exception as e:
                error_msg = str(e)
                self.log_error(playlist_id, video['video_id'], 
                             f"Erro inesperado:\n{error_msg}")
                print(f"Erro inesperado: {error_msg}")
                return False
        
        return False

    def retry_failed_downloads(self):
        """Tenta baixar novamente os vídeos que falharam anteriormente"""
        print("\nVerificando vídeos com falha...")
        total_retried = 0
        total_success = 0
        
        for playlist_id, playlist_data in self.progress['playlists'].items():
            if 'failed_videos' not in playlist_data or not playlist_data['failed_videos']:
                continue
                
            print(f"\nRetentando downloads da playlist: {playlist_data['title']}")
            failed_videos = playlist_data['failed_videos'].copy()
            
            for video_id in failed_videos:
                # Encontra o vídeo e sua posição na playlist
                videos = self.get_playlist_videos(playlist_id)
                video_info = next((v for v in videos if v['video_id'] == video_id), None)
                
                if not video_info:
                    print(f"Vídeo {video_id} não encontrado na playlist, removendo da lista de falhas...")
                    playlist_data['failed_videos'].remove(video_id)
                    continue
                
                position = video_info['position']
                print(f"\nTentando novamente: {video_info['title']}")
                total_retried += 1
                
                if self.download_video(video_info, playlist_id, position, len(videos)):
                    print(f"Download bem sucedido: {video_info['title']}")
                    playlist_data['failed_videos'].remove(video_id)
                    playlist_data['downloaded_videos'].append(video_id)
                    playlist_data['completed_videos'] = len(playlist_data['downloaded_videos'])
                    total_success += 1
                    
                    # Atualiza o status da playlist se todos os vídeos foram baixados
                    if len(playlist_data['downloaded_videos']) == playlist_data['total_videos']:
                        playlist_data['status'] = 'completed'
                    
                    self.save_progress()
                    time.sleep(10)  # Pausa entre tentativas bem sucedidas
                
            if not playlist_data['failed_videos']:
                print(f"Todos os vídeos com falha da playlist {playlist_data['title']} foram recuperados!")
        
        if total_retried > 0:
            print(f"\nResumo de retentativas:")
            print(f"Total de vídeos tentados novamente: {total_retried}")
            print(f"Downloads recuperados com sucesso: {total_success}")
        else:
            print("\nNenhum vídeo com falha encontrado para tentar novamente.")

    def download_playlist(self, playlist_id, playlist_title):
        """Baixa todos os vídeos de uma playlist, mantendo o progresso"""
        print(f"\nIniciando download da playlist: {playlist_title}")
        
        try:
            # Verifica e retoma downloads existentes
            videos = self.verify_and_resume_downloads(playlist_id, playlist_title)
            if not videos:
                print("Não foi possível obter a lista de vídeos da playlist")
                return
                
            total_videos = len(videos)
            progress = self.progress['playlists'][playlist_id]
            
            # Se a playlist já estiver completa, pula
            if progress['status'] == 'completed':
                print(f"Playlist já está completa: {playlist_title}")
                return
            
            # Retoma do último vídeo baixado com sucesso
            start_pos = progress['last_position'] + 1
            
            # Processa os vídeos restantes
            for i, video in enumerate(videos[start_pos:], start=start_pos):
                if video['video_id'] in progress['downloaded_videos']:
                    print(f"Vídeo {i+1}/{total_videos} já baixado, pulando...")
                    continue
                
                print(f"\nBaixando {i+1}/{total_videos}: {video['title']}")
                if self.download_video(video, playlist_id, i, total_videos):
                    progress['downloaded_videos'].append(video['video_id'])
                    progress['last_position'] = i
                    progress['completed_videos'] = len(progress['downloaded_videos'])
                    
                    # Remove da lista de falhas se existir
                    if 'failed_videos' in progress and video['video_id'] in progress['failed_videos']:
                        progress['failed_videos'].remove(video['video_id'])
                    
                    self.save_progress()
                    print(f"Download concluído ({i+1}/{total_videos}): {video['title']}")
                    self.display_progress(playlist_id, len(progress['downloaded_videos']), total_videos)
                    time.sleep(5)  # Pausa maior entre downloads
                else:
                    print(f"Falha no download de {video['title']}")
                    if 'failed_videos' not in progress:
                        progress['failed_videos'] = []
                    if video['video_id'] not in progress['failed_videos']:
                        progress['failed_videos'].append(video['video_id'])
                    self.save_progress()
            
            # Atualiza status final
            if len(progress['downloaded_videos']) == total_videos:
                progress['status'] = 'completed'
                self.save_progress()
                print(f"\nPlaylist {playlist_title} concluída!")
            
        except Exception as e:
            print(f"Erro ao processar playlist {playlist_title}: {str(e)}")
            import traceback
            traceback.print_exc()

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

        # Após tentar todas as playlists, tenta recuperar os downloads que falharam
        self.retry_failed_downloads()

    def verify_and_resume_downloads(self, playlist_id, playlist_title):
        """Verifica os downloads existentes e retoma de onde parou"""
        print(f"\nVerificando downloads da playlist: {playlist_title}")
        
        # Garante que temos o registro da playlist no progresso
        if playlist_id not in self.progress['playlists']:
            self.progress['playlists'][playlist_id] = {
                'title': playlist_title,
                'downloaded_videos': [],
                'status': 'in_progress',
                'last_position': -1,
                'total_videos': 0,
                'completed_videos': 0,
                'failed_videos': []
            }
            self.save_progress()
        
        # Verifica os arquivos físicos existentes
        playlist_path, _ = prepare_playlist_structure(playlist_id)
        existing_files = list(playlist_path.glob('*.mp3'))
        
        # Obtém a lista de vídeos da playlist com várias tentativas
        max_retries = 5
        retry_count = 0
        videos = None
        
        while retry_count < max_retries:
            try:
                print(f"Tentativa {retry_count + 1} de obter lista de vídeos...")
                videos = self.get_playlist_videos(playlist_id)
                break
            except Exception as e:
                retry_count += 1
                wait_time = 10 * (2 ** (retry_count - 1))
                print(f"Erro ao obter lista de vídeos: {str(e)}")
                if retry_count < max_retries:
                    print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    raise Exception("Não foi possível obter a lista de vídeos após várias tentativas")
        
        # Atualiza o total de vídeos
        total_videos = len(videos)
        self.progress['playlists'][playlist_id]['total_videos'] = total_videos
        
        # Verifica cada vídeo
        for video in videos:
            video_id = video['video_id']
            position = video['position']
            position_str = str(position + 1).zfill(len(str(total_videos)))
            
            # Procura por arquivos correspondentes
            expected_pattern = f"{position_str} - *.mp3"
            matching_files = list(playlist_path.glob(expected_pattern))
            
            if matching_files and any(f.stat().st_size > 1024 for f in matching_files):
                # Arquivo existe e tem tamanho adequado
                if video_id not in self.progress['playlists'][playlist_id]['downloaded_videos']:
                    print(f"Arquivo encontrado para vídeo {video_id}, atualizando progresso...")
                    self.progress['playlists'][playlist_id]['downloaded_videos'].append(video_id)
                    self.progress['playlists'][playlist_id]['last_position'] = position
                    self.progress['playlists'][playlist_id]['completed_videos'] = len(self.progress['playlists'][playlist_id]['downloaded_videos'])
            else:
                # Arquivo não existe ou está corrompido
                if video_id in self.progress['playlists'][playlist_id]['downloaded_videos']:
                    print(f"Arquivo não encontrado para vídeo marcado como baixado: {video_id}")
                    self.progress['playlists'][playlist_id]['downloaded_videos'].remove(video_id)
                    if video_id not in self.progress['playlists'][playlist_id].get('failed_videos', []):
                        self.progress['playlists'][playlist_id].setdefault('failed_videos', []).append(video_id)
        
        # Atualiza o status geral
        completed = len(self.progress['playlists'][playlist_id]['downloaded_videos'])
        self.progress['playlists'][playlist_id]['completed_videos'] = completed
        
        if completed == total_videos:
            self.progress['playlists'][playlist_id]['status'] = 'completed'
        else:
            self.progress['playlists'][playlist_id]['status'] = 'in_progress'
        
        self.save_progress()
        self.display_progress(playlist_id, completed, total_videos)
        
        return videos

def main():
    downloader = PlaylistDownloader()
    downloader.download_all_playlists()

if __name__ == '__main__':
    main()
