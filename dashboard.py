import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, timedelta
import os
import pytz

# 🔹 CONFIGURAÇÕES DO SUPABASE
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# 🔹 Conectar ao Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔹 Função para buscar dados do Supabase
def buscar_dados():
    response = supabase.table("tesouro_direto").select("*").execute()
    data = response.data
    return pd.DataFrame(data)

# 🔹 Carregar os dados
df = buscar_dados()

# 🔹 Converter data_atualizacao para formato datetime
df["data_atualizacao"] = pd.to_datetime(df["data_atualizacao"])

# 🔹 Usar fuso horário do Brasil (BRT)
fuso_brasil = pytz.timezone('America/Sao_Paulo')
hoje_brasil = datetime.now(fuso_brasil).date()

# 🔹 Criar seletor de data
st.sidebar.title("Configurações")
# Pegando todas as datas únicas disponíveis nos dados
datas_disponiveis = sorted(df["data_atualizacao"].dt.date.unique())
# Se não houver dados disponíveis, use a data de hoje
if not datas_disponiveis:
    datas_disponiveis = [hoje_brasil]

# Opção para selecionar a data ou usar "Hoje"
usar_hoje = st.sidebar.checkbox("Usar data de hoje", value=True)
if usar_hoje:
    data_selecionada = hoje_brasil
    # Verificar se há dados para hoje
    if hoje_brasil not in datas_disponiveis:
        st.sidebar.warning(f"⚠️ Não há dados disponíveis para hoje ({hoje_brasil.strftime('%d/%m/%Y')})")
        if datas_disponiveis:
            data_selecionada = datas_disponiveis[-1]  # Use a data mais recente disponível
else:
    # Se não usar "hoje", mostrar seletor de data
    data_index = 0
    if datas_disponiveis and datas_disponiveis[-1] != hoje_brasil:
        data_index = len(datas_disponiveis) - 1  # Seleciona a data mais recente por padrão
    
    data_selecionada = st.sidebar.selectbox(
        "Selecione a data:",
        datas_disponiveis,
        index=data_index,
        format_func=lambda x: x.strftime("%d/%m/%Y")
    )

# 🔹 Filtrar dados pela data selecionada
df_filtrado = df[df["data_atualizacao"].dt.date == data_selecionada]

# 🔹 Criar tabela dinâmica (Pivot Table)
if not df_filtrado.empty:
    # Criar uma cópia da coluna data_atualizacao para usar apenas o horário
    df_filtrado["horario"] = df_filtrado["data_atualizacao"].dt.strftime("%H:%M")
    
    # Usar o horário nas colunas em vez da data_atualizacao completa
    df_pivot = df_filtrado.pivot_table(index=["tipo", "vencimento"], 
                                   columns="horario", 
                                   values="taxa", 
                                   aggfunc="mean")  # Usa a média caso tenha múltiplos valores
    
    # Formatação da data para o título
    data_formatada = data_selecionada.strftime("%d/%m/%Y")
else:
    df_pivot = pd.DataFrame()  # Garante que a tabela fica vazia caso não haja dados
    data_formatada = data_selecionada.strftime("%d/%m/%Y")

# 🔹 Exibir a Pivot Table no Dashboard com a data no título
st.subheader(f"📊 Tesouro Direto - Taxas do Dia {data_formatada}")
if not df_pivot.empty:
    st.dataframe(df_pivot.style.format("{:.2f}"), use_container_width=True)  # Exibir com duas casas decimais
else:
    st.warning(f"⚠️ Nenhuma atualização disponível para {data_formatada}.")
