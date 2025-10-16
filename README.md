# 🎵 YouTube Audio Downloader & Repository Manager

Sistema completo para download, organização e gerenciamento de áudios do YouTube com sincronização inteligente e controle de duplicatas.

## 🎯 **OBJETIVO DO PROJETO**

Criar um sistema automatizado que:
1. **Sincroniza** dados do YouTube (playlists + vídeos individuais)
2. **Elimina duplicatas** inteligentemente (prioriza playlists)
3. **Baixa áudios** organizados por playlist
4. **Upload** para repositório centralizado
5. **Gerencia** espaço em disco automaticamente
6. **Monitora** progresso em tempo real

## 🏗️ **ARQUITETURA ATUAL**

### **📁 Estrutura de Pastas**
```
downloadYOUTUBE/
├── 📂 downloads/
│   └── 📂 audio/          # Downloads locais (temporários)
├── 📂 playlists/          # Metadados das playlists
│   ├── playlists_metadata.json    # 302 playlists
│   ├── playlist_videos.json       # 4.395 vídeos detalhados
│   └── playlist_downloader.py     # Sistema de download
├── 🔐 client_secret.json  # Credenciais YouTube API
├── 🔑 token.json          # Token de autenticação
├── 🍪 cookies.txt         # Cookies para download
├── 📄 unique_video_urls.txt       # 460 vídeos únicos
├── 📄 filtered_playlist_urls.txt  # 301 playlists filtradas
└── 📄 excluded_playlists.json     # Playlists excluídas
```

### **🔄 Fluxo de Trabalho Atualizado**
```
1. Sincronização → 2. Filtragem → 3. Download → 4. Upload → 5. Limpeza
```

## 🚀 **FUNCIONALIDADES PRINCIPAIS**

### **🔄 Sistema de Sincronização**
- ✅ **Sincronização completa** com YouTube Data API
- ✅ **Atualização de playlists** (302 playlists)
- ✅ **Atualização de vídeos** (4.395 vídeos em playlists)
- ✅ **Vídeos individuais** (3.885 vídeos do canal)
- ✅ **Detecção automática** de duplicatas

### **🎯 Sistema Anti-Duplicatas**
- ✅ **Priorização de playlists** (mais organizadas)
- ✅ **Vídeos únicos individuais** (460 vídeos não duplicados)
- ✅ **Lista unificada** sem duplicatas
- ✅ **Economia de 41%** nos downloads (3.425 duplicatas evitadas)

### **�� Sistema de Download**
- ✅ **Download de áudios** em alta qualidade (MP3)
- ✅ **Organização automática** por playlist
- ✅ **Resumo de downloads** interrompidos
- ✅ **Sanitização de nomes** de arquivos
- ✅ **Progresso em tempo real**

### **📤 Sistema de Upload**
- ✅ **Upload automático** para repositório
- ✅ **Exclusão local** após upload
- ✅ **Log de uploads** com metadados
- ✅ **Upload em lotes** configurável
- ✅ **Reversão de uploads** se necessário

### **🗂️ Gerenciamento de Repositório**
- ✅ **Sincronização** de repositório
- ✅ **Controle de espaço** (manter X playlists)
- ✅ **Mover playlists** antigas de volta
- ✅ **Estatísticas** de uso

### **📊 Monitoramento**
- ✅ **Interface web** (Streamlit)
- ✅ **Logs detalhados** de operações
- ✅ **Status em tempo real**
- ✅ **Relatórios** de progresso

## 🛠️ **SCRIPTS PRINCIPAIS**

### **🔄 Sincronização e Dados**
| Script | Função | Uso |
|--------|--------|-----|
| `main.py` | Autenticação inicial | `python3 main.py` |
| `main_playlist.py` | Gerenciar playlists | `python3 main_playlist.py` |
| `update_youtube_data.py` | Sincronizar com YouTube | Integrado |
| `download_unified.py` | Download sem duplicatas | `python3 download_unified.py` |

### **📥 Download Específico**
| Script | Função | Uso |
|--------|--------|-----|
| `download_individual_videos.py` | Vídeos individuais | `python3 download_individual_videos.py` |
| `playlists/playlist_downloader.py` | Download de áudios | Integrado |
| `streamlit_app.py` | Interface web | `streamlit run streamlit_app.py` |

### **📤 Upload e Repositório**
| Script | Função | Uso |
|--------|--------|-----|
| `upload_simple.py` | Upload simples | `python3 upload_simple.py` |
| `upload_batch.py` | Upload em lotes | `python3 upload_batch.py --batch 10` |
| `sync_repository.py` | Sincronizar repo | `python3 sync_repository.py --sync` |
| `revert_uploads.py` | Reverter uploads | `python3 revert_uploads.py` |

### **🔧 Utilitários**
| Script | Função | Uso |
|--------|--------|-----|
| `fix_filenames.py` | Corrigir nomes | `python3 fix_filenames.py` |
| `youtube_authenticator.py` | Autenticação | Integrado |
| `metadata_manager.py` | Gerenciar metadados | Integrado |

## ⚙️ **CONFIGURAÇÃO INICIAL**

### **1. Instalação de Dependências**
```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **2. Configuração da API do YouTube**
```bash
# 1. Criar projeto no Google Cloud Console
# 2. Ativar YouTube Data API v3
# 3. Criar credenciais OAuth 2.0
# 4. Baixar client_secret.json
# 5. Colocar no diretório raiz do projeto
```

### **3. Configuração do Repositório**
```bash
# Definir caminho do repositório (padrão)
REPOSITORY_PATH="/Users/bno/Documents/Repositorio/public/repositorio/audios/"
```

## 📋 **GUIA DE USO ATUALIZADO**

### **🚀 Iniciando o Sistema**
```bash
# 1. Autenticação
python3 main.py

# 2. Sincronizar com YouTube
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)

# 3. Download unificado (sem duplicatas)
python3 download_unified.py
```

### **🔄 Sincronização de Dados**
```bash
# Sincronização completa
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)

# Opções individuais:
# 2. Atualizar lista de playlists
# 3. Atualizar links dos vídeos das playlists
# 4. Atualizar vídeos individuais do canal
```

### **📥 Download Inteligente**
```bash
# Opção 1: Download unificado (recomendado)
python3 download_unified.py
# Escolher: 3. Baixar tudo (playlists + vídeos únicos)

# Opção 2: Download específico
python3 main_playlist.py
# Escolher: 7. Baixar uma playlist específica
```

### **📤 Upload para Repositório**
```bash
# Upload simples (todas as playlists prontas)
python3 upload_simple.py

# Upload em lotes (10 playlists por vez)
python3 upload_batch.py --batch 10

# Ver status dos uploads
python3 upload_batch.py --status
```

### **🗂️ Gerenciar Repositório**
```bash
# Sincronizar repositório (manter 20 playlists)
python3 sync_repository.py --sync
# Digite: 20

# Reverter uploads
python3 revert_uploads.py
# Escolher opção desejada
```

## 📊 **ESTRUTURA DE DADOS ATUALIZADA**

### **📄 playlists/playlists_metadata.json**
```json
[
  {
    "id": "PLO_7Zoueaxd6QB0mwEhFN1bXLiAniHDrS",
    "title": "Acumulação da Prática do Buda da Medicina",
    "description": "Ensinamentos sobre...",
    "publishedAt": "2023-01-01T00:00:00Z",
    "itemCount": 1839
  }
]
```

### **📄 playlists/playlist_videos.json**
```json
{
  "PLAYLIST_ID": {
    "title": "Nome da Playlist",
    "videos": [
      {
        "video_id": "VIDEO_ID",
        "title": "Título do Vídeo",
        "description": "Descrição...",
        "publishedAt": "2023-01-01T00:00:00Z",
        "position": 1
      }
    ],
    "total_videos": 10
  }
}
```

### **📄 unique_video_urls.txt**
```
https://www.youtube.com/watch?v=WlBie6yLhNE
https://www.youtube.com/watch?v=F8jR4Y-LK3Q
...
```

### **📄 excluded_playlists.json**
```json
[
  {
    "id": "PLO_7Zoueaxd6QB0mwEhFN1bXLiAniHDrS",
    "title": "Acumulação da Prática do Buda da Medicina",
    "video_count": 1839,
    "reason": "Playlist muito grande - 1839 vídeos"
  }
]
```

## 🎯 **SISTEMA ANTI-DUPLICATAS**

### **📊 Estatísticas de Duplicatas**
- **Total de vídeos únicos:** 4.855
- **Vídeos em playlists:** 4.395 (prioritários)
- **Vídeos únicos individuais:** 460
- **Duplicatas evitadas:** 3.425 (41% de economia)

### **🔄 Lógica de Priorização**
1. **Playlists têm prioridade** (mais organizadas)
2. **Vídeos individuais** = apenas os que NÃO estão em playlists
3. **Zero duplicatas** garantidas
4. **Download mais eficiente**

### **📁 Arquivos de Lista Unificada**
- `playlist_urls.txt` - 302 playlists (todas)
- `filtered_playlist_urls.txt` - 301 playlists (filtradas)
- `unique_video_urls.txt` - 460 vídeos únicos
- `excluded_playlists.json` - Playlists excluídas

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **📁 Caminhos Personalizados**
```python
# Em upload_simple.py, upload_batch.py, sync_repository.py
REPOSITORY_PATH = "/caminho/para/seu/repositorio/"
```

### **📊 Limites de Upload**
```python
# Em upload_batch.py
DEFAULT_BATCH_SIZE = 10  # Playlists por lote
MAX_REPOSITORY_SIZE = 20  # Máximo no repositório
```

### **🎵 Qualidade de Áudio**
```python
# Em playlist_downloader.py
AUDIO_QUALITY = "best"  # best, worst, 320k, 256k, 192k, 128k
```

### **🚫 Gerenciar Playlists Excluídas**
```bash
# Editar manualmente
nano excluded_playlists.json

# Ou usar o sistema integrado
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)
```

## 🛡️ **SISTEMA DE SANITIZAÇÃO**

### **🚫 Caracteres Problemáticos Removidos**
- Aspas duplas e simples (`"`, `'`)
- Aspas Unicode (`"`, `"`, `'`, `'`)
- Caracteres especiais (`<`, `>`, `:`, `/`, `\`, `|`, `?`, `*`)
- Espaços múltiplos e hífens

### **✅ Exemplo de Sanitização**
```
Antes: Retiro "Visão Profunda das Oito Consciências como Caminho" CEBB Maceió
Depois: Retiro Visão Profunda das Oito Consciências como Caminho CEBB Maceió
```

## 📈 **MONITORAMENTO E ESTATÍSTICAS**

### **🌐 Interface Web (Streamlit)**
```bash
streamlit run streamlit_app.py
```
- 📊 Dashboard em tempo real
- 📈 Gráficos de progresso
- 📋 Lista de playlists
- 🔄 Status de downloads

### **📊 Comandos de Status**
```bash
# Status geral
python3 upload_batch.py --status

# Estatísticas de sincronização
python3 update_youtube_data.py
# Escolher: 5. Mostrar estatísticas

# Verificar playlists disponíveis
python3 main_playlist.py
# Escolher: 5. Listar todas as playlists
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **❌ Problemas Comuns**

**1. Erro de Autenticação**
```bash
# Reautenticar
rm token.json
python3 main.py
```

**2. Canal não encontrado**
```bash
# Verificar ID do canal
python3 -c "from youtube_authenticator import YouTubeAuthenticator; print('Canal ID correto')"
```

**3. Playlist não encontrada**
```bash
# Sincronizar dados
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)
```

**4. Erro de upload**
```bash
# Verificar permissões do repositório
ls -la /caminho/para/repositorio/
```

**5. Nomes de arquivo problemáticos**
```bash
# Corrigir nomes
python3 fix_filenames.py
```

### **🔍 Logs e Debug**
```bash
# Ver logs de download
tail -f downloads/audio/download_errors.log

# Ver logs de upload
python3 upload_batch.py --status

# Verificar sincronização
python3 update_youtube_data.py
# Escolher: 5. Mostrar estatísticas
```

## 🔒 **SEGURANÇA E BOAS PRÁTICAS**

### **🔐 Credenciais**
- ✅ **Nunca commitar** `client_secret.json` e `token.json`
- ✅ **Usar .gitignore** para arquivos sensíveis
- ✅ **Rotacionar tokens** periodicamente

### **💾 Backup**
- ✅ **Backup regular** do repositório
- ✅ **Versionamento** dos scripts
- ✅ **Logs de auditoria** de uploads

### **🚀 Performance**
- ✅ **Downloads paralelos** limitados
- ✅ **Limpeza automática** de arquivos temporários
- ✅ **Monitoramento** de uso de disco
- ✅ **Sistema anti-duplicatas** eficiente

## 📚 **CASOS DE USO ATUALIZADOS**

### **🎯 Caso 1: Setup Inicial Completo**
```bash
# 1. Autenticar
python3 main.py

# 2. Sincronizar com YouTube
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)

# 3. Download unificado
python3 download_unified.py
# Escolher: 3. Baixar tudo (playlists + vídeos únicos)

# 4. Monitorar progresso
streamlit run streamlit_app.py
```

### **🎯 Caso 2: Upload para Repositório**
```bash
# 1. Upload em lotes
python3 upload_batch.py --batch 10

# 2. Sincronizar repositório
python3 sync_repository.py --sync
# Digite: 20 (manter 20 playlists)

# 3. Verificar status
python3 upload_batch.py --status
```

### **🎯 Caso 3: Manutenção e Atualização**
```bash
# 1. Atualizar dados do YouTube
python3 main_playlist.py
# Escolher: 1. Sincronizar com YouTube (COMPLETO)

# 2. Corrigir nomes problemáticos
python3 fix_filenames.py

# 3. Reverter uploads se necessário
python3 revert_uploads.py

# 4. Limpar repositório
python3 sync_repository.py --sync
```

### **🎯 Caso 4: Download Específico**
```bash
# Download apenas de playlists
python3 download_unified.py
# Escolher: 1. Baixar todas as playlists

# Download apenas de vídeos únicos
python3 download_unified.py
# Escolher: 2. Baixar vídeos individuais únicos

# Download de vídeo individual
python3 download_individual_videos.py
# Escolher: 1. Baixar vídeo individual
```

## 🤝 **CONTRIBUIÇÃO**

### **📝 Como Contribuir**
1. **Fork** o repositório
2. **Criar branch** para feature
3. **Implementar** mudanças
4. **Testar** thoroughly
5. **Submit** pull request

### **🐛 Reportar Bugs**
- 📧 **Descrição detalhada** do problema
- 📋 **Passos para reproduzir**
- 📊 **Logs relevantes**
- 💻 **Sistema operacional**

## 📞 **SUPORTE**

### **📚 Documentação**
- 📖 **README.md** - Este arquivo
- 💻 **Código comentado** - Scripts principais
- 🔍 **Logs detalhados** - Para debugging

### **🆘 Ajuda**
- 🔍 **Verificar logs** primeiro
- 📋 **Usar comandos de status**
- 🛠️ **Scripts de diagnóstico** disponíveis

---

## 🎉 **RESUMO EXECUTIVO ATUALIZADO**

Este sistema oferece uma solução completa e inteligente para:
- ✅ **Sincronização automática** com YouTube Data API
- ✅ **Sistema anti-duplicatas** (41% de economia)
- ✅ **Download inteligente** priorizando playlists
- ✅ **Organização automática** por playlist
- ✅ **Upload gerenciado** para repositório centralizado
- ✅ **Controle de espaço** em disco
- ✅ **Monitoramento** em tempo real
- ✅ **Sistema robusto** com tratamento de erros

### **📊 Estatísticas Atuais:**
- **302 playlists** disponíveis
- **4.395 vídeos** em playlists
- **460 vídeos únicos** individuais
- **4.855 vídeos únicos** total
- **3.425 duplicatas** evitadas

**🚀 Sistema otimizado e pronto para uso em produção!**

## 🛑 **SISTEMA DE INTERRUPÇÃO GRACIOSA**

### **🎯 Como Funciona**
O sistema agora captura `Ctrl + C` e oferece opções inteligentes:

```
⚠️  INTERRUPÇÃO DETECTADA!
==================================================
Você pressionou Ctrl+C. O que deseja fazer?

1. Finalizar download atual e salvar progresso
2. Continuar o download
3. Forçar saída imediata

Escolha uma opção (1-3):
```

### **✅ Opções Disponíveis**

**1. Finalizar download atual e salvar progresso**
- ✅ Salva o progresso atual
- ✅ Para o download graciosamente
- ✅ Permite retomar depois
- ✅ Não perde dados

**2. Continuar o download**
- ✅ Ignora a interrupção
- ✅ Continua de onde parou
- ✅ Útil para interrupções acidentais

**3. Forçar saída imediata**
- ⚠️ Para imediatamente
- ⚠️ Salva progresso básico
- ⚠️ Use apenas se necessário

### **🔄 Como Retomar Downloads**

```bash
# Opção 1: Menu principal
python3 main_playlist.py
# Escolher: 8. Retomar downloads incompletos

# Opção 2: Download unificado
python3 download_unified.py
# Escolher: 3. Baixar tudo (playlists + vídeos únicos)
```

### **🧪 Testar o Sistema**

```bash
# Script de demonstração
python3 test_graceful_interrupt.py
# Pressione Ctrl+C para testar
```

### **💡 Dicas Importantes**

1. **Sempre use a opção 1** para parar graciosamente
2. **Progresso é salvo automaticamente** a cada vídeo
3. **Downloads podem ser retomados** a qualquer momento
4. **Sistema funciona em todos os scripts** de download
5. **Ctrl+C duas vezes** força saída imediata

