import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime
import os

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

# 🔹 Filtrar apenas os dados do dia corrente
hoje = datetime.now().date()
df_hoje = df[df["data_atualizacao"].dt.date == hoje]

# 🔹 Criar tabela dinâmica (Pivot Table)
if not df_hoje.empty:
    # Criar uma cópia da coluna data_atualizacao para usar apenas o horário
    df_hoje["horario"] = df_hoje["data_atualizacao"].dt.strftime("%H:%M")
    
    # Usar o horário nas colunas em vez da data_atualizacao completa
    df_pivot = df_hoje.pivot_table(index=["tipo", "vencimento"], 
                                   columns="horario", 
                                   values="taxa", 
                                   aggfunc="mean")  # Usa a média caso tenha múltiplos valores
    
    # Formatação da data para o título
    data_formatada = hoje.strftime("%d/%m/%Y")
else:
    df_pivot = pd.DataFrame()  # Garante que a tabela fica vazia caso não haja dados
    data_formatada = hoje.strftime("%d/%m/%Y")

# 🔹 Exibir a Pivot Table no Dashboard com a data no título
st.subheader(f"📊 Tesouro Direto - Taxas do Dia {data_formatada}")
if not df_pivot.empty:
    st.dataframe(df_pivot.style.format("{:.2f}"), use_container_width=True)  # Exibir com duas casas decimais
else:
    st.warning("⚠️ Nenhuma atualização disponível para hoje.")
