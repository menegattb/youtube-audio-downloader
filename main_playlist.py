#!/usr/bin/env python3
"""
Sistema principal de gerenciamento de playlists do YouTube
Com sistema de interrupção graciosa
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from playlists.playlist_downloader import PlaylistDownloader
from update_youtube_data import YouTubeDataUpdater
from graceful_interrupt import check_interrupt, reset_interrupt, cleanup_interrupt

def show_menu():
    """Exibe o menu principal"""
    print("\n" + "="*60)
    print("🎵 SISTEMA DE DOWNLOAD DE PLAYLISTS DO YOUTUBE")
    print("="*60)
    print("1. Sincronizar com YouTube (COMPLETO)")
    print("2. Atualizar lista de playlists")
    print("3. Atualizar links dos vídeos das playlists")
    print("4. Atualizar vídeos individuais (MÉTODO MELHORADO)")
    print("5. Listar todas as playlists")
    print("6. Baixar todas as playlists")
    print("7. Baixar uma playlist específica")
    print("8. Retomar downloads incompletos")
    print("9. Mostrar estatísticas")
    print("10. Upload para repositório")
    print("11. Sincronizar repositório")
    print("0. Sair")
    print("="*60)

def get_user_choice():
    """Obtém a escolha do usuário"""
    while True:
        try:
            choice = input("\nEscolha uma opção (0-11): ").strip()
            if choice.isdigit() and 0 <= int(choice) <= 11:
                return int(choice)
            else:
                print("❌ Opção inválida. Digite um número entre 0 e 11.")
        except KeyboardInterrupt:
            print("\n\n🛑 Operação cancelada pelo usuário.")
            return 0

def sync_youtube_data():
    """Sincroniza dados com YouTube"""
    print("\n🔄 SINCRONIZAÇÃO COMPLETA COM YOUTUBE")
    print("="*50)
    
    updater = YouTubeDataUpdater()
    
    try:
        print("1. Atualizando lista de playlists...")
        updater.update_playlists()
        
        if check_interrupt():
            print("🛑 Sincronização interrompida pelo usuário")
            return
        
        print("2. Atualizando vídeos das playlists...")
        updater.update_playlist_videos()
        
        if check_interrupt():
            print("🛑 Sincronização interrompida pelo usuário")
            return
        
        print("3. Atualizando vídeos individuais...")
        updater.get_all_channel_videos()
        
        if check_interrupt():
            print("🛑 Sincronização interrompida pelo usuário")
            return
        
        print("4. Mostrando estatísticas...")
        updater.show_statistics()
        
        print("\n✅ Sincronização completa finalizada!")
        
    except Exception as e:
        print(f"❌ Erro durante sincronização: {e}")
        import traceback
        traceback.print_exc()

def update_playlists():
    """Atualiza lista de playlists"""
    print("\n📋 ATUALIZANDO LISTA DE PLAYLISTS")
    print("="*40)
    
    updater = YouTubeDataUpdater()
    updater.update_playlists()

def update_playlist_videos():
    """Atualiza vídeos das playlists"""
    print("\n🎬 ATUALIZANDO VÍDEOS DAS PLAYLISTS")
    print("="*40)
    
    updater = YouTubeDataUpdater()
    updater.update_playlist_videos()

def update_individual_videos():
    """Atualiza vídeos individuais"""
    print("\n🎵 ATUALIZANDO VÍDEOS INDIVIDUAIS")
    print("="*40)
    
    updater = YouTubeDataUpdater()
    updater.get_all_channel_videos()

def list_playlists():
    """Lista todas as playlists"""
    print("\n📋 LISTANDO TODAS AS PLAYLISTS")
    print("="*40)
    
    updater = YouTubeDataUpdater()
    updater.show_statistics()

def download_all_playlists():
    """Baixa todas as playlists"""
    print("\n⬇️ BAIXANDO TODAS AS PLAYLISTS")
    print("="*40)
    print("💡 Dica: Pressione Ctrl+C para interromper graciosamente")
    print("="*40)
    
    downloader = PlaylistDownloader()
    
    try:
        downloader.download_all_playlists()
    except KeyboardInterrupt:
        print("\n🛑 Download interrompido pelo usuário")
    finally:
        downloader.cleanup()

def download_specific_playlist():
    """Baixa uma playlist específica"""
    print("\n🎯 BAIXANDO PLAYLIST ESPECÍFICA")
    print("="*40)
    
    # Lista playlists disponíveis
    updater = YouTubeDataUpdater()
    playlists = updater.get_playlists()
    
    if not playlists:
        print("❌ Nenhuma playlist encontrada. Execute a sincronização primeiro.")
        return
    
    print("\nPlaylists disponíveis:")
    for i, playlist in enumerate(playlists[:20], 1):  # Mostra apenas as primeiras 20
        print(f"{i}. {playlist['title']} ({playlist['itemCount']} vídeos)")
    
    if len(playlists) > 20:
        print(f"... e mais {len(playlists) - 20} playlists")
    
    try:
        choice = input(f"\nEscolha uma playlist (1-{min(20, len(playlists))}): ").strip()
        if not choice.isdigit():
            print("❌ Opção inválida")
            return
        
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < min(20, len(playlists)):
            selected_playlist = playlists[choice_idx]
            print(f"\nBaixando: {selected_playlist['title']}")
            
            downloader = PlaylistDownloader()
            try:
                downloader.download_playlist(selected_playlist['id'], selected_playlist['title'])
            finally:
                downloader.cleanup()
        else:
            print("❌ Opção inválida")
    
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

def resume_downloads():
    """Retoma downloads incompletos"""
    print("\n🔄 RETOMANDO DOWNLOADS INCOMPLETOS")
    print("="*40)
    print("💡 Dica: Pressione Ctrl+C para interromper graciosamente")
    print("="*40)
    
    downloader = PlaylistDownloader()
    
    try:
        downloader.resume_incomplete_downloads()
    except KeyboardInterrupt:
        print("\n🛑 Retomada interrompida pelo usuário")
    finally:
        downloader.cleanup()

def show_statistics():
    """Mostra estatísticas"""
    print("\n📊 ESTATÍSTICAS DO SISTEMA")
    print("="*40)
    
    updater = YouTubeDataUpdater()
    updater.show_statistics()

def upload_to_repository():
    """Upload para repositório"""
    print("\n📤 UPLOAD PARA REPOSITÓRIO")
    print("="*40)
    print("Escolha uma opção:")
    print("1. Upload simples (todas as playlists)")
    print("2. Upload em lotes")
    print("3. Reverter uploads")
    
    try:
        choice = input("Escolha (1-3): ").strip()
        
        if choice == "1":
            import subprocess
            subprocess.run([sys.executable, "upload_simple.py"])
        elif choice == "2":
            import subprocess
            subprocess.run([sys.executable, "upload_batch.py"])
        elif choice == "3":
            import subprocess
            subprocess.run([sys.executable, "revert_uploads.py"])
        else:
            print("❌ Opção inválida")
    
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

def sync_repository():
    """Sincroniza repositório"""
    print("\n🔄 SINCRONIZANDO REPOSITÓRIO")
    print("="*40)
    
    try:
        import subprocess
        subprocess.run([sys.executable, "sync_repository.py"])
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando sistema de download de playlists...")
    
    # Configura interrupção graciosa
    reset_interrupt()
    
    try:
        while True:
            show_menu()
            choice = get_user_choice()
            
            if choice == 0:
                print("\n👋 Encerrando sistema...")
                break
            elif choice == 1:
                sync_youtube_data()
            elif choice == 2:
                update_playlists()
            elif choice == 3:
                update_playlist_videos()
            elif choice == 4:
                update_individual_videos()
            elif choice == 5:
                list_playlists()
            elif choice == 6:
                download_all_playlists()
            elif choice == 7:
                download_specific_playlist()
            elif choice == 8:
                resume_downloads()
            elif choice == 9:
                show_statistics()
            elif choice == 10:
                upload_to_repository()
            elif choice == 11:
                sync_repository()
            
            if choice != 0:
                input("\nPressione Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_interrupt()

if __name__ == "__main__":
    main()
