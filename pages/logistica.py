import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Logistica.load_Logistica import load_ordemcar_from_sql
import psycopg2 as psy
import pandas as pd
import streamlit as st


def carregar_dados():
    """Carrega os dados da planilha CSV e os armazena no estado da sessão."""
    if 'df_ordemcar' not in st.session_state:
        df_ordemcar = load_ordemcar_from_sql()
        st.session_state.df_ordemcar = df_ordemcar

        

def resumo_geral():
    """Exibe o resumo geral de eficiência das operações."""
    df = st.session_state.df_ordemcar

    total_embarques = len(df)
    entregas_no_prazo = df[df['status'] == 'Entregue no prazo'].shape[0] if 'status' in df.columns else 0
    percentual_no_prazo = (entregas_no_prazo / total_embarques * 100) if total_embarques > 0 else 0
    frota_utilizada = df['codveiculo'].nunique() if 'codveiculo' in df.columns else 0
    frota_total = 100  # Exemplo: total de veículos disponíveis
    taxa_utilizacao = (frota_utilizada / frota_total * 100) if frota_total > 0 else 0

    st.header("Resumo Geral")
    st.metric("Total de Embarques", total_embarques)
    st.metric("Percentual de Entregas no Prazo", f"{percentual_no_prazo:.2f}%")
    st.metric("Taxa de Utilização de Frota", f"{taxa_utilizacao:.2f}%")

def status_conhecimentos():
    """Exibe o status de conhecimentos e ordens."""
    df = st.session_state.df_ordemcar

    status_counts = df['status'].value_counts() if 'status' in df.columns else pd.Series()
    st.header("Status de Conhecimentos e Ordens")
    st.bar_chart(status_counts)

def custo_operacional():
    """Exibe a análise de custos operacionais."""
    df = st.session_state.df_ordemcar

    if 'fretemotorista' in df.columns and 'precotonmotorista' in df.columns:
        custo_total_motorista = df['fretemotorista'].sum() + df['precotonmotorista'].sum()
    else:
        custo_total_motorista = 0

    st.header("Custo Operacional")
    st.metric("Custo Total com Motoristas", f"R${custo_total_motorista:,.2f}")

def logistica_geografica():
    """Exibe a análise logística por unidade e região."""
    df = st.session_state.df_ordemcar

    if 'codcidadeorigem' in df.columns and 'codcidadedestino' in df.columns:
        regioes = df.groupby(['codcidadeorigem', 'codcidadedestino']).size().reset_index(name='Quantidade')
        st.header("Logística Geográfica")
        st.dataframe(regioes)

def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    carregar_dados()

    st.title("Dashboard de Logística Operacional")

    resumo_geral()
    status_conhecimentos()
    custo_operacional()
    logistica_geografica()

if __name__ == "__main__":
    main()
