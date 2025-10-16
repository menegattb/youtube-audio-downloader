#!/usr/bin/env python3
"""
Sistema de interrupção graciosa para downloads
Captura Ctrl+C e pergunta se o usuário quer finalizar o download
"""

import signal
import sys
import threading
import time

class GracefulInterrupt:
    def __init__(self):
        self.interrupt_requested = False
        self.interrupt_confirmed = False
        self.original_sigint = None
        self.setup_signal_handler()
    
    def setup_signal_handler(self):
        """Configura o handler para capturar Ctrl+C"""
        self.original_sigint = signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handler para Ctrl+C"""
        if self.interrupt_requested:
            # Segunda vez - força a saída
            print("\n\n🛑 Forçando saída...")
            sys.exit(1)
        
        self.interrupt_requested = True
        print("\n\n⚠️  INTERRUPÇÃO DETECTADA!")
        print("=" * 50)
        print("Você pressionou Ctrl+C. O que deseja fazer?")
        print()
        print("1. Finalizar download atual e salvar progresso")
        print("2. Continuar o download")
        print("3. Forçar saída imediata")
        print()
        
        while True:
            try:
                choice = input("Escolha uma opção (1-3): ").strip()
                
                if choice == "1":
                    print("\n✅ Finalizando download graciosamente...")
                    print("💾 Salvando progresso...")
                    self.interrupt_confirmed = True
                    return
                elif choice == "2":
                    print("\n▶️  Continuando download...")
                    self.interrupt_requested = False
                    return
                elif choice == "3":
                    print("\n🛑 Forçando saída...")
                    sys.exit(1)
                else:
                    print("❌ Opção inválida. Digite 1, 2 ou 3.")
            except KeyboardInterrupt:
                # Se pressionar Ctrl+C novamente, força saída
                print("\n\n🛑 Forçando saída...")
                sys.exit(1)
    
    def should_stop(self):
        """Verifica se deve parar o download"""
        return self.interrupt_confirmed
    
    def reset(self):
        """Reseta o estado para permitir nova interrupção"""
        self.interrupt_requested = False
        self.interrupt_confirmed = False
    
    def cleanup(self):
        """Restaura o handler original"""
        if self.original_sigint:
            signal.signal(signal.SIGINT, self.original_sigint)

# Instância global
graceful_interrupt = GracefulInterrupt()

def check_interrupt():
    """Função para verificar se deve parar (para usar em loops)"""
    return graceful_interrupt.should_stop()

def reset_interrupt():
    """Reseta o estado de interrupção"""
    graceful_interrupt.reset()

def cleanup_interrupt():
    """Limpa o handler de interrupção"""
    graceful_interrupt.cleanup()
