#!/usr/bin/env python3
"""
Script para download unificado sem duplicatas
Prioriza playlists e baixa apenas vídeos individuais únicos
"""

import subprocess
import sys
from pathlib import Path

def download_playlists():
    """Baixa todas as playlists"""
    print("🎵 BAIXANDO TODAS AS PLAYLISTS")
    print("=" * 50)
    
    playlist_file = Path("playlist_urls.txt")
    if not playlist_file.exists():
        print("❌ Arquivo playlist_urls.txt não encontrado!")
        return False
    
    # Conta quantas playlists existem
    with open(playlist_file, 'r') as f:
        playlists = [line.strip() for line in f if line.strip()]
    
    print(f"📋 {len(playlists)} playlists encontradas")
    
    # Baixa cada playlist
    for i, playlist_url in enumerate(playlists, 1):
        print(f"\n[{i}/{len(playlists)}] Baixando playlist...")
        print(f"URL: {playlist_url}")
        
        try:
            # Comando yt-dlp para baixar playlist como áudio
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--output", "downloads/audio/%(playlist_title)s/%(title)s.%(ext)s",
                "--cookies", "cookies.txt",
                playlist_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Playlist baixada com sucesso!")
            else:
                print(f"❌ Erro ao baixar playlist: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return True

def download_unique_individuals():
    """Baixa apenas vídeos individuais únicos"""
    print("\n�� BAIXANDO VÍDEOS INDIVIDUAIS ÚNICOS")
    print("=" * 50)
    
    video_file = Path("unique_video_urls.txt")
    if not video_file.exists():
        print("❌ Arquivo unique_video_urls.txt não encontrado!")
        return False
    
    # Conta quantos vídeos únicos existem
    with open(video_file, 'r') as f:
        videos = [line.strip() for line in f if line.strip()]
    
    print(f"🎵 {len(videos)} vídeos únicos encontrados")
    
    # Baixa cada vídeo
    for i, video_url in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Baixando vídeo...")
        print(f"URL: {video_url}")
        
        try:
            # Comando yt-dlp para baixar vídeo como áudio
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--output", "downloads/audio/Vídeos Individuais/%(title)s.%(ext)s",
                "--cookies", "cookies.txt",
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Vídeo baixado com sucesso!")
            else:
                print(f"❌ Erro ao baixar vídeo: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return True

def show_statistics():
    """Mostra estatísticas dos arquivos"""
    print("\n📊 ESTATÍSTICAS DOS ARQUIVOS")
    print("=" * 50)
    
    playlist_file = Path("playlist_urls.txt")
    video_file = Path("unique_video_urls.txt")
    
    if playlist_file.exists():
        with open(playlist_file, 'r') as f:
            playlists = [line.strip() for line in f if line.strip()]
        print(f"📋 Playlists: {len(playlists)}")
    
    if video_file.exists():
        with open(video_file, 'r') as f:
            videos = [line.strip() for line in f if line.strip()]
        print(f"🎵 Vídeos únicos individuais: {len(videos)}")
    
    total = len(playlists) + len(videos) if playlist_file.exists() and video_file.exists() else 0
    print(f"📊 Total de conteúdo único: {total}")

def main():
    print("�� DOWNLOAD UNIFICADO SEM DUPLICATAS")
    print("=" * 50)
    print("Este script prioriza playlists e baixa apenas vídeos únicos!")
    
    while True:
        print("\nOpções:")
        print("1. Baixar todas as playlists")
        print("2. Baixar vídeos individuais únicos")
        print("3. Baixar tudo (playlists + vídeos únicos)")
        print("4. Mostrar estatísticas")
        print("5. Sair")
        
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == "1":
            download_playlists()
        
        elif choice == "2":
            download_unique_individuals()
        
        elif choice == "3":
            print("🚀 Iniciando download completo...")
            if download_playlists():
                download_unique_individuals()
            print("✅ Download completo finalizado!")
        
        elif choice == "4":
            show_statistics()
        
        elif choice == "5":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
