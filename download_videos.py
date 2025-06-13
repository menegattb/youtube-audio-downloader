import subprocess
import time
from pathlib import Path

def download_video(video_id, title):
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", "downloads/audio/%(title)s.%(ext)s",
        url
    ]
    
    try:
        subprocess.run(cmd, check=True)
        # Se chegou aqui, o download foi bem sucedido
        with open('downloads/audio/download_progress.txt', 'a') as f:
            f.write(f"{video_id}\n")
        return True
    except subprocess.CalledProcessError:
        print(f"Erro ao baixar {video_id} - {title}")
        return False

def main():
    with open('pending_downloads.txt', 'r') as f:
        pending = [line.strip().split('\t') for line in f if line.strip()]
    
    total = len(pending)
    for i, (video_id, title) in enumerate(pending, 1):
        print(f"\nBaixando {i}/{total}: {title}")
        success = download_video(video_id, title)
        if not success:
            print("Falha no download, tentando próximo...")
        time.sleep(2)  # Pequena pausa entre downloads

if __name__ == '__main__':
    main()
