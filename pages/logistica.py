import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_teste_from_sql  # Tabela de conhecimento
from faturamento.fatura.load_data.load_contas import load_conta_from_sql
from faturamento.fatura.load_data.load_clientes import load_clientes_from_sql
import datetime

def carregar_dados():
    """Carrega os dados de conhecimento e armazena no estado da sessão, sem usar ordemcar."""
    if 'df_conhecimento' not in st.session_state:
        df_conhecimento = load_teste_from_sql()
        st.session_state.df_conhecimento = df_conhecimento

def resumo_geral():
    """Exibe o resumo geral de eficiência das operações, usando o DataFrame filtrado."""
    df = st.session_state.df_conhecimento_filtrado

    total_embarques = len(df)
    
    
    # Se houver uma coluna 'codveiculo' para analisar frota
    frota_utilizada = df['codveiculo'].nunique() if 'codveiculo' in df.columns else 0
    frota_total = 100  # Exemplo fixo
    # taxa_utilizacao = (frota_utilizada / frota_total * 100) if frota_total > 0 else 0

    st.header("Resumo Geral - Conhecimentos (Filtrado)")
    st.metric("Total de Conhecimentos", total_embarques)
    st.metric("Total de Carros utilizados", frota_utilizada)
    # st.metric("Taxa de Utilização de Frota", f"{taxa_utilizacao:.2f}%")


def custo_operacional():
    """Exibe a análise de custos operacionais, incluindo freteMotorista e pedágio, usando o DataFrame filtrado."""
    df = st.session_state.df_conhecimento_filtrado
    st.header("Custo Operacional - Conhecimentos (Filtrado)")

    # Gasto total com Frete Motorista
    custo_frete_motorista = df['fretemotorista'].sum() if 'fretemotorista' in df.columns else 0

    # Gasto total com Pedágio (ajuste o nome da coluna caso seja diferente)
    custo_pedagio = df['valorpedagio'].sum() if 'valorpedagio' in df.columns else 0
    
    st.metric("Custo Total Frete Motorista", f"R${custo_frete_motorista:,.2f}")
    st.metric("Custo Total Pedágio", f"R${custo_pedagio:,.2f}")
    
    custo_total = custo_frete_motorista + custo_pedagio
    st.metric("Custo Total Geral", f"R${custo_total:,.2f}")

def logistica_geografica():
    """Exibe a análise logística por origem/destino usando o DataFrame filtrado."""
    df = st.session_state.df_conhecimento_filtrado

    st.header("Logística Geográfica - Conhecimentos (Filtrado)")
    if 'codcidadeorigem' in df.columns and 'codcidadedestino' in df.columns:
        regioes = (
            df.groupby(['codcidadeorigem', 'codcidadedestino'])
            .size()
            .reset_index(name='Quantidade')
        )
        st.dataframe(regioes)
    else:
        st.info("Não há colunas 'codcidadeorigem' e/ou 'codcidadedestino' no df_conhecimento.")


def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    carregar_dados()

    st.title("Dashboard de Logística Operacional - (Somente Tabela de Conhecimento)")

    # 1) Pegamos o DataFrame original
    df_original = st.session_state.df_conhecimento

    # 2) Se existir a coluna 'data', convertemos para datetime e aplicamos filtro
    if 'data' in df_original.columns:
        # Converte para datetime (caso ainda não esteja)
        df_original['data'] = pd.to_datetime(df_original['data'], errors='coerce')
        
        # Determina os limites mínimo e máximo da coluna data
        min_data = df_original['data'].min()
        max_data = df_original['data'].max()
        
        # Definimos o intervalo padrão como 'semana passada'
        hoje = datetime.date.today()
        uma_semana_atras = hoje - datetime.timedelta(days=7)
        
        # Garante que o range inicial não fique fora do [min_data, max_data]
        # Convertendo min_data / max_data para "date" se forem datetime
        min_data_date = min_data.date() if not pd.isnull(min_data) else hoje
        max_data_date = max_data.date() if not pd.isnull(max_data) else hoje
        
        default_start = max(min_data_date, uma_semana_atras)
        default_end = min(max_data_date, hoje)
        
        # Cria um filtro de intervalo de datas (com valor padrão = semana passada)
        st.subheader("Filtro de Data")
        data_range = st.date_input(
            "Selecione o intervalo:",
            [default_start, default_end]
        )

        if len(data_range) == 2:
            start_date, end_date = data_range
            # Aplica a máscara no dataFrame
            mask = (
                (df_original['data'] >= pd.to_datetime(start_date)) &
                (df_original['data'] <= pd.to_datetime(end_date))
            )
            df_filtrado = df_original[mask]
        else:
            df_filtrado = df_original
    else:
        st.info("A tabela não possui coluna 'data'.")
        df_filtrado = df_original

    # 3) Armazena o DataFrame filtrado em session_state
    st.session_state.df_conhecimento_filtrado = df_filtrado

    # 4) Chama as funções que trabalharão com df_conhecimento_filtrado
    resumo_geral()
    custo_operacional()
    logistica_geografica()


if __name__ == "__main__":
    main()
