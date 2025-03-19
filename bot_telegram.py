from telethon.sync import TelegramClient, events
import re
from supabase import create_client, Client

# 🔹 CONFIGURAÇÕES DO TELEGRAM
API_ID = "29658342"  # Substitua pelo seu API_ID
API_HASH = "5040071b496b3ee01128a3e000be2015"  # Substitua pelo seu API_HASH
BOT_TOKEN = "7107922566:AAEvpKZ-yze2Z1MPND-K-_7R849s8ZpveLA"  # Pegue do BotFather

# 🔹 CONFIGURAÇÕES DO SUPABASE
SUPABASE_URL = "https://ashrwswtamtkhxkkamro.supabase.co"  # Cole a URL do Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzaHJ3c3d0YW10a2h4a2thbXJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI0MjAxNjksImV4cCI6MjA1Nzk5NjE2OX0.MR_OF9z2H6JXzwX_rYiRn3pIKII-Xgs7bOh7Ietf_wA"  # Cole a chave API (anon key)



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
