import json
import os
from pathlib import Path

def main():
    # Carregar metadados
    with open('video_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Mapear video_ids para títulos
    video_id_to_title = {item['video_id']: item['title'] for item in metadata}
    
    # Listar arquivos MP3 existentes
    audio_dir = Path('downloads/audio')
    mp3_files = list(audio_dir.glob('*.mp3'))
    
    # Criar conjunto de IDs já baixados
    downloaded_ids = set()
    for file in mp3_files:
        for video_id in video_id_to_title.keys():
            if video_id in str(file):
                downloaded_ids.add(video_id)
    
    # Atualizar arquivo de progresso
    with open('downloads/audio/download_progress.txt', 'w', encoding='utf-8') as f:
        for video_id in sorted(downloaded_ids):
            f.write(f"{video_id}\n")

    # Criar lista de downloads pendentes
    pending_downloads = []
    for item in metadata:
        if item['video_id'] not in downloaded_ids:
            pending_downloads.append((item['video_id'], item['title']))
    
    # Salvar lista de downloads pendentes
    with open('pending_downloads.txt', 'w', encoding='utf-8') as f:
        for video_id, title in pending_downloads:
            f.write(f"{video_id}\t{title}\n")

    print(f"Total de vídeos nos metadados: {len(metadata)}")
    print(f"Vídeos já baixados: {len(downloaded_ids)}")
    print(f"Vídeos pendentes: {len(pending_downloads)}")

if __name__ == '__main__':
    main()
