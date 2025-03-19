import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# 🔹 CONFIGURAÇÕES DO SUPABASE
SUPABASE_URL = "https://ifjxlelguuujvabcgnjm.supabase.co"  # Cole a URL do Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlmanhsZWxndXV1anZhYmNnbmptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIzOTM2MjAsImV4cCI6MjA1Nzk2OTYyMH0.wv0alf5lXG4Fo4oeycGFibl_9b4wGb9on6FT_Zgl0V8"  # Cole a chave API (anon key)

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
    df_pivot = df_hoje.pivot_table(index=["tipo", "vencimento"], 
                                   columns="data_atualizacao", 
                                   values="taxa", 
                                   aggfunc="mean")  # Usa a média caso tenha múltiplos valores
else:
    df_pivot = pd.DataFrame()  # Garante que a tabela fica vazia caso não haja dados

# 🔹 Exibir a Pivot Table no Dashboard
st.subheader("📊 Tabela Dinâmica - Taxas do Dia Corrente")
if not df_pivot.empty:
    st.dataframe(df_pivot.style.format("{:.2f}"))  # Exibir com duas casas decimais
else:
    st.warning("⚠️ Nenhuma atualização disponível para hoje.")
