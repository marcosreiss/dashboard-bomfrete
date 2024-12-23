import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_fatura_from_sql

from datetime import datetime, date

def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_tabela' not in st.session_state:
        df_tabela = load_fatura_from_sql()
        st.session_state.df_tabela = df_tabela
        st.write("Colunas carregadas no DataFrame:", st.session_state.df_tabela.columns.tolist())

        # Verificar e converter a coluna 'data' para datetime
        if "data" in st.session_state.df_tabela.columns:
            st.session_state.df_tabela["data"] = pd.to_datetime(st.session_state.df_tabela["data"], errors='coerce')
        else:
            st.error("A coluna 'data' não foi encontrada no DataFrame!")

def calcular_indicadores(df_filtrado):
    """Calcula e exibe indicadores com base no intervalo de tempo."""
    col1, col2, col3 = st.columns(3)
    
    # Indicadores gerais
    with col1:
        total_registros = df_filtrado.shape[0]
        st.metric("Total de Registros", total_registros)
    
    with col2:
        total_frete_empresa = df_filtrado["freteempresa"].sum()
        st.metric("Total Frete Empresa", f"R${total_frete_empresa:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    with col3:
        total_frete_motorista = df_filtrado["fretemotorista"].sum()
        st.metric("Total Frete Motorista", f"R${total_frete_motorista:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    # Indicadores adicionais
    col4, col5, col6 = st.columns(3)
    
    with col4:
        total_cancelados = df_filtrado[df_filtrado["cancelado"] == "S"].shape[0]
        st.metric("Cancelados", total_cancelados)
    
    with col5:
        total_peso_saida = df_filtrado["pesosaida"].sum()
        st.metric("Peso Saída", f"{total_peso_saida:.2f} kg")
    
    with col6:
        total_peso_chegada = df_filtrado["pesochegada"].sum()
        st.metric("Peso Chegada", f"{total_peso_chegada:.2f} kg")
    
def gerar_graficos(df_filtrado):
    """Gera gráficos com base nos dados filtrados."""
    import plotly.express as px
    
    # Gráfico de barras - Faturamento por cliente
    fig1 = px.bar(
        df_filtrado.groupby("codcliente")["freteempresa"].sum().reset_index(),
        x="codcliente",
        y="freteempresa",
        title="Faturamento por Cliente",
        labels={"freteempresa": "Frete Empresa", "codcliente": "Cliente"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de linhas - Evolução do Frete por Data
    fig2 = px.line(
        df_filtrado.groupby("data")["freteempresa"].sum().reset_index(),
        x="data",
        y="freteempresa",
        title="Evolução do Frete (Empresa)",
        labels={"freteempresa": "Frete Empresa", "data": "Data"},
    )
    st.plotly_chart(fig2, use_container_width=True)

def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    load_data()
    
    st.title("Dashboard Financeiro - Análise de Fretes e Emissões")
    
    st.header("Filtro de Intervalo de Tempo")
    data_inicio, data_fim = st.date_input(
        "Selecione o intervalo de tempo",
        value=(date(2024, 1, 1), date(2024, 12, 31)),  # Corrigido para usar 'date'
        min_value=date(2010, 1, 1),
        max_value=date(2050, 12, 31)
    )
    
    # Filtro de dados com base no intervalo
    df_filtrado = st.session_state.df_tabela.copy()
    df_filtrado = df_filtrado[(df_filtrado["data"] >= pd.Timestamp(data_inicio)) & (df_filtrado["data"] <= pd.Timestamp(data_fim))]

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado no intervalo selecionado.")
        return
    
    # Calcular e exibir os indicadores
    calcular_indicadores(df_filtrado)
    
    # Geração de gráficos
    st.header("Gráficos")
    gerar_graficos(df_filtrado)

if __name__ == "__main__":
    main()
