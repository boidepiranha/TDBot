# TDBot - Telegram Dashboard Bot

Um bot para Telegram com dashboard para monitoramento e controle.

## Funcionalidades

- Bot interativo para Telegram
- Dashboard para visualização e controle
- Interface web para gerenciamento

## Requisitos

- Python 3.7+
- Bibliotecas necessárias em `requirements.txt`

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente:
   - Copie o arquivo `bot_telegram.env.example` para `bot_telegram.env`
   - Preencha com suas credenciais:
     - API_ID e API_HASH: Obtenha em https://my.telegram.org/apps
     - BOT_TOKEN: Obtenha através do @BotFather no Telegram
     - SUPABASE_URL e SUPABASE_KEY: Obtenha no seu projeto Supabase
4. Execute o bot:
   ```
   python bot_telegram.py
   ```

## Dashboard

Para iniciar o dashboard:
```
python dashboard.py
```

## Segurança

- Nunca compartilhe seu arquivo `.env` ou credenciais
- Não comite arquivos de ambiente (.env) no Git
- O arquivo `.gitignore` está configurado para excluir arquivos sensíveis 