#!/usr/bin/env python3
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from youtube_authenticator import YouTubeAuthenticator
from graceful_interrupt import check_interrupt, reset_interrupt, cleanup_interrupt
import json
import os
import subprocess
import time
from datetime import datetime

def sanitize_folder_name(name):
    """Remove caracteres problemáticos do nome da pasta"""
    # Caracteres problemáticos que causam problemas em sistemas de arquivos
    problematic_chars = {
        '"': '',      # Aspas duplas
        "'": '',      # Aspas simples
        '"': '',      # Aspas duplas Unicode
        '"': '',      # Aspas duplas Unicode
        ''': '',      # Aspas simples Unicode
        ''': '',      # Aspas simples Unicode
        '‹': '',      # Aspas angulares
        '›': '',      # Aspas angulares
        '«': '',      # Aspas duplas angulares
        '»': '',      # Aspas duplas angulares
        '<': '',      # Menor que
        '>': '',      # Maior que
        ':': '-',     # Dois pontos
        '/': '-',     # Barra
        '\\': '-',    # Barra invertida
        '|': '-',     # Pipe
        '?': '',      # Interrogação
        '*': '',      # Asterisco
        '\n': ' ',    # Quebra de linha
        '\r': ' ',    # Retorno de carro
        '\t': ' ',    # Tab
    }
    
    # Aplica as substituições
    sanitized = name
    for char, replacement in problematic_chars.items():
        sanitized = sanitized.replace(char, replacement)
    
    # Remove espaços múltiplos e espaços no início/fim
    import re
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

class PlaylistDownloader:
    def __init__(self):
        self.youtube = YouTubeAuthenticator()
        self.progress_file = Path(__file__).parent / 'playlist_progress.json'
        self.names_file = Path(__file__).parent / 'playlist_names.json'
        self.excluded_file = root_dir / 'excluded_playlists.json'
        self.progress = self.load_progress()
        self.playlist_names = self.load_playlist_names()
        self.excluded_playlists = self.load_excluded_playlists()
        self.downloads_dir = root_dir / 'downloads' / 'audio'
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuração de interrupção graciosa
        reset_interrupt()
    
    def load_progress(self):
        """Carrega o progresso dos downloads"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar progresso: {e}")
                return {"playlists": {}}
        return {"playlists": {}}
    
    def load_playlist_names(self):
        """Carrega o mapeamento de IDs para nomes das playlists"""
        if self.names_file.exists():
            try:
                with open(self.names_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar nomes das playlists: {e}")
                return {}
        return {}
    
    def load_excluded_playlists(self):
        """Carrega a lista de playlists excluídas"""
        if self.excluded_file.exists():
            try:
                with open(self.excluded_file, 'r', encoding='utf-8') as f:
                    excluded_data = json.load(f)
                    # Retorna apenas os IDs das playlists excluídas
                    return [playlist['id'] for playlist in excluded_data]
            except Exception as e:
                print(f"Erro ao carregar playlists excluídas: {e}")
                return []
        return []
    
    def save_progress(self):
        """Salva o progresso dos downloads"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar progresso: {e}")
    
    def save_playlist_names(self):
        """Salva o mapeamento de IDs para nomes das playlists"""
        try:
            with open(self.names_file, 'w', encoding='utf-8') as f:
                json.dump(self.playlist_names, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar nomes das playlists: {e}")
    
    def get_playlist_name(self, playlist_id, default_title=None):
        """Obtém o nome legível de uma playlist pelo ID"""
        if playlist_id in self.playlist_names:
            return self.playlist_names[playlist_id]
        elif default_title:
            # Salva o nome padrão se não existir
            self.playlist_names[playlist_id] = default_title
            self.save_playlist_names()
            return default_title
        else:
            return f"Playlist {playlist_id}"
    
    def get_playlist_videos(self, playlist_id):
        """Obtém a lista de vídeos de uma playlist"""
        try:
            videos_file = Path(__file__).parent / 'playlist_videos.json'
            if not videos_file.exists():
                print("Arquivo de vídeos das playlists não encontrado")
                return []
            
            with open(videos_file, 'r', encoding='utf-8') as f:
                all_playlists = json.load(f)
            
            if playlist_id not in all_playlists:
                print(f"Playlist {playlist_id} não encontrada")
                return []
            
            return all_playlists[playlist_id]['videos']
        except Exception as e:
            print(f"Erro ao obter vídeos da playlist: {e}")
            return []
    
    def log_error(self, playlist_id, video_id, error_msg):
        """Registra erros de download"""
        error_log = self.downloads_dir / 'download_errors.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] PLAYLIST: {playlist_id}\n")
            f.write(f"VIDEO: {video_id}\n")
            f.write(f"ERRO: {error_msg}\n")
            f.write("-" * 50 + "\n")
    
    def check_download_status(self, playlist_dir, video_id):
        """Verifica se o download foi bem sucedido"""
        try:
            # Procura pelo arquivo com o ID do vídeo
            output_file = playlist_dir / f"{video_id}.mp3"
            
            if not output_file.exists():
                return False, f"Arquivo não encontrado: {output_file}"
            
            # Verifica se o arquivo tem tamanho mínimo (1KB)
            if output_file.stat().st_size < 1024:
                return False, f"Arquivo muito pequeno (possivelmente corrompido): {output_file.stat().st_size} bytes"
            
            return True, f"Download bem sucedido: {output_file.name} ({output_file.stat().st_size} bytes)"
            
        except Exception as e:
            return False, f"Erro na verificação: {str(e)}"
    
    def display_progress(self, playlist_id, completed, total):
        """Exibe o progresso do download"""
        percentage = (completed / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * completed // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        playlist_name = self.get_playlist_name(playlist_id)
        print(f"\r[{playlist_id[:8]}...] |{bar}| {completed}/{total} ({percentage:.1f}%) - {playlist_name[:30]}...", end='', flush=True)
    
    def download_video(self, video, playlist_id, position, total_videos):
        """Baixa um vídeo individual"""
        # Verifica se deve parar
        if check_interrupt():
            print(f"\n🛑 Download interrompido pelo usuário")
            return False
        
        # Cria o diretório da playlist usando ID
        playlist_dir = self.downloads_dir / playlist_id
        playlist_dir.mkdir(parents=True, exist_ok=True)
        
        # Template de saída
        output_template = str(playlist_dir / f"%(id)s.%(ext)s")
        
        # Configurações de retry
        max_retries = 3
        retry_count = 0
        retry_delay = 10
        
        while retry_count < max_retries:
            # Verifica se deve parar antes de cada tentativa
            if check_interrupt():
                print(f"\n🛑 Download interrompido pelo usuário")
                return False
            
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
                
                playlist_name = self.get_playlist_name(playlist_id)
                print(f"Iniciando download de: {video['title']}")
                print(f"Playlist: {playlist_name}")
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                
                # Verifica se o download foi realmente bem sucedido
                success, error_msg = self.check_download_status(playlist_dir, video['video_id'])
                if not success:
                    raise Exception(f"Falha na verificação do download: {error_msg}")
                
                print(f"✅ Download concluído: {video['title']}")
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
                    
                    # Verifica interrupção durante a espera
                    for _ in range(wait_time):
                        if check_interrupt():
                            print(f"\n🛑 Download interrompido pelo usuário")
                            return False
                        time.sleep(1)
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
            # Verifica se deve parar
            if check_interrupt():
                print(f"\n🛑 Retentativas interrompidas pelo usuário")
                return
            
            if 'failed_videos' not in playlist_data or not playlist_data['failed_videos']:
                continue
                
            playlist_name = self.get_playlist_name(playlist_id)
            print(f"\nRetentando downloads da playlist: {playlist_name}")
            failed_videos = playlist_data['failed_videos'].copy()
            
            for video_id in failed_videos:
                # Verifica se deve parar
                if check_interrupt():
                    print(f"\n🛑 Retentativas interrompidas pelo usuário")
                    return
                
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
                print(f"Todos os vídeos com falha da playlist {playlist_name} foram recuperados!")
        
        if total_retried > 0:
            print(f"\nResumo de retentativas:")
            print(f"Total de vídeos tentados novamente: {total_retried}")
            print(f"Downloads recuperados com sucesso: {total_success}")
        else:
            print("\nNenhum vídeo com falha encontrado para tentar novamente.")

    def download_playlist(self, playlist_id, playlist_title):
        """Baixa todos os vídeos de uma playlist, mantendo o progresso"""
        playlist_name = self.get_playlist_name(playlist_id, playlist_title)
        print(f"\nIniciando download da playlist: {playlist_name}")
        print(f"ID da playlist: {playlist_id}")
        
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
                print(f"Playlist já está completa: {playlist_name}")
                return
            
            # Retoma do último vídeo baixado com sucesso
            start_pos = progress['last_position'] + 1
            
            # Processa os vídeos restantes
            for i, video in enumerate(videos[start_pos:], start=start_pos):
                # Verifica se deve parar antes de cada vídeo
                if check_interrupt():
                    print(f"\n🛑 Download da playlist interrompido pelo usuário")
                    print(f"💾 Progresso salvo: {progress['completed_videos']}/{total_videos} vídeos")
                    return
                
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
                print(f"\nPlaylist {playlist_name} concluída!")
            
        except Exception as e:
            print(f"Erro ao processar playlist {playlist_name}: {str(e)}")
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
            # Verifica se deve parar antes de cada playlist
            if check_interrupt():
                print(f"\n🛑 Download de playlists interrompido pelo usuário")
                print(f"💾 Progresso salvo: {completed}/{total_playlists} playlists processadas")
                return
            
            completed += 1
            playlist_id = playlist['id']
            title = playlist['title']
            
            print(f"\n=== Playlist {completed}/{total_playlists} ===")
            
            # Verifica se a playlist está na lista de exclusão
            if playlist_id in self.excluded_playlists:
                print(f"🚫 Playlist excluída: {title}")
                print(f"   Motivo: Listada em excluded_playlists.json")
                continue
            
            if playlist_id in self.progress['playlists']:
                if self.progress['playlists'][playlist_id]['status'] == 'completed':
                    print(f"Playlist já concluída: {title}")
                    continue
            
            self.download_playlist(playlist_id, title)

        # Após tentar todas as playlists, tenta recuperar os downloads que falharam
        if not check_interrupt():
            self.retry_failed_downloads()

    def verify_and_resume_downloads(self, playlist_id, playlist_title):
        """Verifica os downloads existentes e retoma de onde parou"""
        playlist_name = self.get_playlist_name(playlist_id, playlist_title)
        print(f"\nVerificando downloads da playlist: {playlist_name}")
        
        # Obtém a lista de vídeos
        videos = self.get_playlist_videos(playlist_id)
        if not videos:
            return []
        
        # Inicializa o progresso da playlist se não existir
        if playlist_id not in self.progress['playlists']:
            self.progress['playlists'][playlist_id] = {
                'title': playlist_name,
                'status': 'in_progress',
                'total_videos': len(videos),
                'completed_videos': 0,
                'downloaded_videos': [],
                'failed_videos': [],
                'last_position': -1
            }
            self.save_progress()
        
        # Verifica arquivos existentes usando ID da playlist
        playlist_dir = self.downloads_dir / playlist_id
        if playlist_dir.exists():
            existing_files = list(playlist_dir.glob('*.mp3'))
            print(f"Encontrados {len(existing_files)} arquivos existentes")
            
            # Atualiza a lista de vídeos baixados
            downloaded_videos = []
            for video in videos:
                video_file = playlist_dir / f"{video['video_id']}.mp3"
                if video_file.exists() and video_file.stat().st_size > 1024:
                    downloaded_videos.append(video['video_id'])
            
            # Atualiza o progresso
            progress = self.progress['playlists'][playlist_id]
            progress['downloaded_videos'] = downloaded_videos
            progress['completed_videos'] = len(downloaded_videos)
            progress['last_position'] = len(downloaded_videos) - 1
            
            if len(downloaded_videos) == len(videos):
                progress['status'] = 'completed'
            
            self.save_progress()
            print(f"Progresso atual: {len(downloaded_videos)}/{len(videos)} vídeos baixados")
        
        return videos

    def get_playlist_status(self, playlist_id):
        """Retorna o status de uma playlist"""
        if playlist_id not in self.progress['playlists']:
            return None
        
        return self.progress['playlists'][playlist_id]

    def resume_incomplete_downloads(self):
        """Retoma downloads incompletos"""
        print("\nVerificando downloads incompletos...")
        
        incomplete_playlists = []
        for playlist_id, playlist_data in self.progress['playlists'].items():
            if playlist_data['status'] != 'completed':
                incomplete_playlists.append((playlist_id, playlist_data['title']))
        
        if not incomplete_playlists:
            print("Nenhum download incompleto encontrado.")
            return
        
        print(f"Encontradas {len(incomplete_playlists)} playlists incompletas:")
        for i, (playlist_id, title) in enumerate(incomplete_playlists, 1):
            progress = self.progress['playlists'][playlist_id]
            print(f"{i}. {title} ({progress['completed_videos']}/{progress['total_videos']})")
        
        print("\nRetomando downloads...")
        for playlist_id, title in incomplete_playlists:
            if check_interrupt():
                print(f"\n🛑 Retomada de downloads interrompida pelo usuário")
                return
            self.download_playlist(playlist_id, title)

    def cleanup(self):
        """Limpa recursos e handlers"""
        cleanup_interrupt()

# Função de conveniência para uso externo
def create_downloader():
    """Cria uma instância do downloader"""
    return PlaylistDownloader()

if __name__ == "__main__":
    downloader = PlaylistDownloader()
    try:
        downloader.download_all_playlists()
    finally:
        downloader.cleanup()
