# YouTube Audio Downloader

Este projeto é uma ferramenta Python robusta para baixar áudio de vídeos do YouTube, especialmente desenvolvida para lidar com grandes coleções de vídeos organizados em playlists.

## Funcionalidades

- Autenticação segura com a API do YouTube usando OAuth 2.0
- Coleta automática de todos os vídeos das playlists do usuário
- Suporte a paginação para playlists com mais de 50 vídeos
- Remoção automática de duplicatas
- Download em lote de áudios usando yt-dlp

## Estrutura do Projeto

```
.
├── youtube_authenticator.py  # Gerencia autenticação OAuth 2.0
├── video_fetcher.py         # Coleta IDs de vídeos do YouTube
└── requirements.txt         # Dependências do projeto
```

## Configuração

1. Obtenha suas credenciais OAuth 2.0 do Google Cloud Console:
   - Crie um projeto no [Google Cloud Console](https://console.cloud.google.com)
   - Habilite a YouTube Data API v3
   - Configure as credenciais OAuth 2.0
   - Baixe o arquivo `client_secret.json`

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o coletor de vídeos:
```bash
python video_fetcher.py
```

## Arquivos Gerados

- `token.json`: Armazena o token de acesso OAuth 2.0 (não deve ser compartilhado)
- `video_ids.txt`: Lista de URLs dos vídeos encontrados

## Requisitos

- Python 3.6+
- Credenciais OAuth 2.0 do Google Cloud Console
- Acesso à API do YouTube

## Notas de Segurança

Os seguintes arquivos contêm informações sensíveis e não devem ser compartilhados:
- `client_secret.json`
- `token.json`
