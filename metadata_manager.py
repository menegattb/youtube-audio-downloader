"""
YouTube Video Metadata Manager

Este módulo coleta e organiza os metadados de vídeos do YouTube,
incluindo título, data, descrição, playlist e outras informações relevantes.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import yt_dlp
from youtube_authenticator import YouTubeAuthenticator
from googleapiclient.errors import HttpError

class QuotaExceededException(Exception):
    """Exceção lançada quando a cota da API do YouTube é excedida."""
    pass

class VideoMetadataManager:
    def __init__(self):
        """Inicializa o gerenciador de metadados com autenticação do YouTube."""
        self.authenticator = YouTubeAuthenticator()
        self.youtube = self.authenticator.get_authenticated_service()
        self.metadata_cache: Dict[str, dict] = {}
        self.playlist_cache: Dict[str, dict] = {}
        self._load_cached_progress()

    def _load_cached_progress(self):
        """Carrega o progresso salvo anteriormente, se existir."""
        if os.path.exists("video_metadata.json"):
            try:
                with open("video_metadata.json", 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    for item in cached_data:
                        self.metadata_cache[item['video_id']] = item
                print(f"Carregado cache com {len(self.metadata_cache)} vídeos processados anteriormente.")
            except Exception as e:
                print(f"Erro ao carregar cache: {str(e)}")

    def _save_progress(self, all_metadata: List[dict]):
        """Salva o progresso atual em arquivos JSON e CSV."""
        print("\nSalvando progresso atual...")
        with open("video_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        self._create_csv_summary(all_metadata)

    def _handle_api_error(self, error: HttpError, context: str):
        """Trata erros da API do YouTube."""
        if error.resp.status == 403 and "quotaExceeded" in str(error):
            raise QuotaExceededException(
                "Cota diária da API do YouTube excedida. "
                "O progresso foi salvo. Por favor, tente novamente em 24 horas."
            )
        print(f"Erro na API do YouTube ({context}): {str(error)}")

    def _get_playlist_details(self, playlist_id: str) -> Optional[dict]:
        """Obtém os detalhes de uma playlist."""
        if playlist_id in self.playlist_cache:
            return self.playlist_cache[playlist_id]

        try:
            playlist_response = self.youtube.playlists().list(
                part="snippet",
                id=playlist_id
            ).execute()

            if playlist_response["items"]:
                playlist_info = {
                    "title": playlist_response["items"][0]["snippet"]["title"],
                    "description": playlist_response["items"][0]["snippet"]["description"],
                    "publishedAt": playlist_response["items"][0]["snippet"]["publishedAt"]
                }
                self.playlist_cache[playlist_id] = playlist_info
                return playlist_info
            
            return None

        except HttpError as e:
            print(f"Erro ao obter detalhes da playlist {playlist_id}: {str(e)}")
            return None

    def get_video_metadata(self, video_id: str) -> Optional[dict]:
        """Obtém os metadados de um vídeo específico."""
        if video_id in self.metadata_cache:
            return self.metadata_cache[video_id]

        try:
            video_response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            ).execute()

            if not video_response["items"]:
                print(f"Vídeo não encontrado: {video_id}")
                return None

            video_info = video_response["items"][0]["snippet"]
            content_details = video_response["items"][0]["contentDetails"]

            metadata = {
                "video_id": video_id,
                "title": video_info["title"],
                "description": video_info["description"],
                "publishedAt": video_info["publishedAt"],
                "duration": content_details["duration"],
                "playlists": []
            }

            self.metadata_cache[video_id] = metadata
            return metadata

        except HttpError as e:
            print(f"Erro ao obter metadados do vídeo {video_id}: {str(e)}")
            return None

    def find_video_playlists(self, video_id: str) -> List[dict]:
        """Encontra todas as playlists que contêm um vídeo específico."""
        try:
            playlists = []
            next_page_token = None

            while True:
                playlist_items_response = self.youtube.playlistItems().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for item in playlist_items_response.get("items", []):
                    playlist_id = item["snippet"]["playlistId"]
                    playlist_info = self._get_playlist_details(playlist_id)
                    
                    if playlist_info:
                        playlists.append(playlist_info)

                next_page_token = playlist_items_response.get("nextPageToken")
                if not next_page_token:
                    break

            return playlists

        except HttpError as e:
            print(f"Erro ao buscar playlists para o vídeo {video_id}: {str(e)}")
            return []

    def process_video_ids(self, video_ids_file: str = "video_ids.txt") -> None:
        """Processa todos os IDs de vídeo do arquivo e coleta seus metadados."""
        print("Iniciando coleta de metadados...")
        all_metadata = []
        
        with open(video_ids_file, 'r') as f:
            video_urls = f.readlines()

        total_videos = len(video_urls)
        processed_count = len(self.metadata_cache)
        print(f"Total de vídeos: {total_videos}, já processados: {processed_count}")

        try:
            for i, url in enumerate(video_urls, 1):
                video_id = url.strip().split('v=')[-1]
                
                # Pula vídeos já processados
                if video_id in self.metadata_cache:
                    all_metadata.append(self.metadata_cache[video_id])
                    continue

                print(f"\rProcessando vídeo {i} de {total_videos}...", end='', flush=True)

                try:
                    metadata = self.get_video_metadata(video_id)
                    if metadata:
                        playlists = self.find_video_playlists(video_id)
                        metadata["playlists"] = playlists
                        all_metadata.append(metadata)

                    # Salva o progresso a cada 10 vídeos
                    if i % 10 == 0:
                        self._save_progress(all_metadata)

                except HttpError as e:
                    self._handle_api_error(e, f"processando vídeo {video_id}")
                    # Se for erro de cota, salva o progresso e encerra
                    if "quotaExceeded" in str(e):
                        self._save_progress(all_metadata)
                        raise QuotaExceededException(
                            f"Cota excedida após processar {i} vídeos. "
                            f"Progresso salvo. Continue mais tarde."
                        )

        except QuotaExceededException as e:
            print(f"\n{str(e)}")
            return

        except Exception as e:
            print(f"\nErro inesperado: {str(e)}")
            self._save_progress(all_metadata)
            return

        print("\nSalvando metadados finais...")
        self._save_progress(all_metadata)
        print("Processo concluído com sucesso!")

    def _create_csv_summary(self, metadata_list: List[dict]) -> None:
        """Cria um arquivo CSV com um resumo dos metadados."""
        import csv
        
        with open("video_metadata.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Video ID', 'Título', 'Data de Publicação', 'Duração', 'Playlists'])
            
            for metadata in metadata_list:
                playlist_names = '; '.join(p['title'] for p in metadata['playlists'])
                writer.writerow([
                    metadata['video_id'],
                    metadata['title'],
                    metadata['publishedAt'],
                    metadata['duration'],
                    playlist_names
                ])

    def download_audio(self, output_dir: str = "downloads/audio", format: str = "mp3", quality: str = "192k") -> None:
        """
        Baixa o áudio dos vídeos que já têm metadados usando yt-dlp e FFmpeg.
        
        Args:
            output_dir (str): Diretório onde os arquivos de áudio serão salvos
            format (str): Formato do áudio (mp3, m4a, etc)
            quality (str): Qualidade do áudio (bitrate)
        """
        if not os.path.exists("video_metadata.json"):
            print("Nenhum metadado encontrado. Execute process_video_ids primeiro.")
            return

        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Carregar metadados
        with open("video_metadata.json", 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)

        total_videos = len(metadata_list)
        print(f"Iniciando download de {total_videos} áudios...")

        # Configurações do yt-dlp
        base_url = "https://www.youtube.com/watch?v="
        
        for i, metadata in enumerate(metadata_list, 1):
            video_id = metadata['video_id']
            video_url = f"{base_url}{video_id}"
            safe_title = "".join(c for c in metadata['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_file = os.path.join(output_dir, f"{safe_title}.{format}")

            # Pular se já existir
            if os.path.exists(output_file):
                print(f"\r[{i}/{total_videos}] Já existe: {safe_title}")
                continue

            print(f"\r[{i}/{total_videos}] Baixando: {safe_title}", end='', flush=True)
            
            try:
                # Configurar comando yt-dlp com FFmpeg
                cmd = [
                    "yt-dlp",
                    "-x",  # Extrair áudio
                    "--audio-format", format,
                    "--audio-quality", quality,
                    "--no-playlist",
                    "-o", output_file,
                    video_url
                ]
                
                # Executar download
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    print(f"\r[{i}/{total_videos}] Concluído: {safe_title}")
                else:
                    print(f"\r[{i}/{total_videos}] Erro ao baixar {safe_title}: {process.stderr}")
                    
            except Exception as e:
                print(f"\r[{i}/{total_videos}] Erro ao baixar {safe_title}: {str(e)}")

        print("\nDownload de áudios concluído!")

    def _progress_hook(self, d):
        """Callback para mostrar o progresso do download."""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percentage = (downloaded / total) * 100
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024  # Converter para MB/s
                    print(f'\rProgresso: {percentage:.1f}% ({speed_mb:.1f} MB/s)', end='', flush=True)
                else:
                    print(f'\rProgresso: {percentage:.1f}%', end='', flush=True)
        elif d['status'] == 'finished':
            print('\rDownload completo! Convertendo...', end='', flush=True)

    def download_audios(self, output_dir: str = "downloads/audio", start_index: int = 0):
        """Faz o download dos áudios dos vídeos que já têm metadados."""
        if not os.path.exists("video_metadata.json"):
            print("Nenhum metadato encontrado. Execute process_video_ids primeiro.")
            return

        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Carregar metadados
        with open("video_metadata.json", 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)

        total_videos = len(metadata_list)
        
        # Contar quantos já foram baixados
        existing_files = len([f for f in os.listdir(output_dir) if f.endswith('.mp3')])
        print(f"Total de vídeos: {total_videos}")
        print(f"Já baixados: {existing_files}")
        print(f"Faltam: {total_videos - existing_files}")
        print("Iniciando downloads pendentes...")

        # Configuração do yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,  # Changed to False to handle errors properly
            'progress_hooks': [self._progress_hook],
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Caminho do FFmpeg no macOS
            'cookiefile': 'cookies.txt',  # Add cookie file support
            'extract_flat': True,  # Avoid downloading playlists
            'retries': 3,  # Number of retries for failed downloads
            'fragment_retries': 3,  # Number of retries for failed fragments
            'skip_unavailable_fragments': False,  # Don't skip unavailable fragments
            'rm_cachedir': True  # Remove cache files after download
        }

        # Arquivo de log para registrar progresso
        log_file = os.path.join(output_dir, 'download_progress.txt')
        downloaded_ids = set()
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                downloaded_ids = set(line.strip() for line in f)

        # Arquivo de log para erros
        error_log_file = os.path.join(output_dir, 'download_errors.txt')
        
        with open(log_file, 'a') as log, open(error_log_file, 'a') as error_log:
            for i, metadata in enumerate(metadata_list[start_index:], start_index + 1):
                video_id = metadata['video_id']

                # Pula vídeos já baixados
                if video_id in downloaded_ids:
                    print(f"\r[{i}/{total_videos}] Já baixado: {metadata['title']}")
                    continue

                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"\r[{i}/{total_videos}] Baixando: {metadata['title']}")

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    log.write(f"{video_id}\n")
                    log.flush()
                    print(f"\r[{i}/{total_videos}] Concluído: {metadata['title']}")
                except Exception as e:
                    error_message = f"{video_id}: {str(e)}"
                    print(f"\r[{i}/{total_videos}] Erro ao baixar {metadata['title']}: {str(e)}")
                    error_log.write(f"{error_message}\n")
                    error_log.flush()
                    
                    if "Sign in to confirm your age" in str(e):
                        print("\nErro de restrição de idade. Certifique-se de que o arquivo cookies.txt contém cookies válidos de uma conta autenticada.")
                    elif "Sign in to confirm you're not a bot" in str(e):
                        print("\nErro de verificação de bot. Certifique-se de que o arquivo cookies.txt contém cookies válidos de uma conta autenticada.")

        print("\nDownload de áudios concluído!")
        print(f"Verifique {error_log_file} para ver os erros encontrados durante o download.")

if __name__ == "__main__":
    try:
        manager = VideoMetadataManager()
        manager.process_video_ids()
    except Exception as e:
        print(f"\nErro durante o processamento: {str(e)}")
