from telethon.sync import TelegramClient, events
import re
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv("bot_telegram.env")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔹 Inicializa os clientes do Telegram e do Supabase
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔹 Função para processar a mensagem encaminhada
from datetime import datetime

def processar_mensagem(mensagem):
    padrao_data = r"📆 (\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})"
    padrao_dados = r"(\d{4})\s+([\d.,]+)%\s+([\d.,]+)"
    dados = []
    tipo_atual = None
    data_atualizacao = None

    for linha in mensagem.split("\n"):
        # Capturar a data e hora da atualização
        match_data = re.search(padrao_data, linha)
        if match_data:
            data_atualizacao = datetime.strptime(
                f"{match_data.group(1)} {match_data.group(2)}", "%d/%m/%Y %H:%M"
            )

        # Identificar a categoria do título (Prefixado, IPCA+, etc.)
        if "Prefixado" in linha:
            tipo_atual = "Prefixado"
        elif "Pré com Juros" in linha:
            tipo_atual = "Pré com Juros"
        elif "IPCA+" in linha and "com Juros" not in linha:
            tipo_atual = "IPCA+"
        elif "IPCA+ com Juros" in linha:
            tipo_atual = "IPCA+ com Juros"
        elif "Renda+" in linha:
            tipo_atual = "Renda+"

        # Extrair os valores numéricos (vencimento, taxa, preço)
        match = re.search(padrao_dados, linha)
        if match and tipo_atual and data_atualizacao:
            vencimento = int(match.group(1))
            taxa = float(match.group(2).replace(",", "."))
            preco = float(match.group(3).replace(",", "."))
            dados.append({
                "data_atualizacao": data_atualizacao.isoformat(),
                "vencimento": vencimento,
                "taxa": taxa,
                "preco": preco,
                "tipo": tipo_atual
            })

    return dados



# 🔹 Função para enviar os dados para o Supabase
def enviar_para_supabase(dados):
    if not dados:
        print("⚠️ Nenhum dado válido encontrado na mensagem.")
        return

    # Pegar a data_atualizacao da primeira entrada (todas terão a mesma)
    data_atualizacao = dados[0]["data_atualizacao"]

    # Verificar se já existe uma entrada com essa data_atualizacao
    resposta = supabase.table("tesouro_direto") \
        .select("id") \
        .eq("data_atualizacao", data_atualizacao) \
        .execute()

    # Se não existir, insere todos os dados da mensagem
    if not resposta.data:
        supabase.table("tesouro_direto").insert(dados).execute()
        print(f"✅ Enviado para Supabase: {len(dados)} registros para {data_atualizacao}")
    else:
        print(f"⚠️ Atualização {data_atualizacao} já existe no banco. Ignorando duplicata.")



# 🔹 Capturar mensagens encaminhadas para o bot
@client.on(events.NewMessage)
async def capturar_mensagem(event):
    if event.message.forward:  # Verifica se a mensagem foi encaminhada
        mensagem = event.message.message
        print(f"📩 Mensagem encaminhada recebida:\n{mensagem}")
        
        dados = processar_mensagem(mensagem)
        
        if dados:
            enviar_para_supabase(dados)

# 🔹 Iniciar o bot
print("🤖 Bot está rodando... Aguardando mensagens encaminhadas.")
client.run_until_disconnected()
