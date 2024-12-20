import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from faturamento.fatura.load_data.load_fatura import load_fatura_from_sql

def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_fatura' not in st.session_state:
        df_fatura = load_fatura_from_sql()
        st.session_state.df_fatura = df_fatura

def calcular_emissoes(tipo_filtro, valores):
    """Calcula a quantidade e o valor total de emissões com base no filtro escolhido."""
    if 'df_fatura' not in st.session_state:
        st.error("Os dados não foram carregados ainda.")
        return 0, "R$0,00"

    df_fatura = st.session_state.df_fatura

    if tipo_filtro == "dia":
        data_especifica = valores[0]
        df_filtrado = df_fatura[df_fatura['data'] == pd.to_datetime(data_especifica)]
    elif tipo_filtro == "mes":
        mes_especifico, ano_especifico = valores
        df_filtrado = df_fatura[(df_fatura['data'].dt.month == mes_especifico) &
                                (df_fatura['data'].dt.year == ano_especifico)]
    elif tipo_filtro == "ano":
        ano_especifico = valores[0]
        df_filtrado = df_fatura[df_fatura['data'].dt.year == ano_especifico]
    elif tipo_filtro == "periodo":
        data_inicio, data_fim = valores
        df_filtrado = df_fatura[(df_fatura['data'] >= pd.to_datetime(data_inicio)) &
                                (df_fatura['data'] <= pd.to_datetime(data_fim))]
    else:
        st.error("Tipo de filtro inválido!")
        return 0, "R$0,00"

    quantidade = df_filtrado.shape[0]
    emissao_total = df_filtrado['valor'].sum()
    emissao_total_formatado = f"R${emissao_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    return quantidade, emissao_total_formatado

def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    load_data()

    st.title("Bomfrete Financeiro")
    st.subheader("Indicadores de emissão")

    tipo_filtro = st.selectbox("Selecione o tipo de filtro", ["dia", "mes", "ano", "periodo"], format_func=lambda x: x.capitalize())

    valores = []
    if tipo_filtro == "dia":
        data_especifica = st.date_input("Selecione o dia")
        if data_especifica:
            valores = [data_especifica]
    elif tipo_filtro == "mes":
        meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        mes_especifico = st.selectbox("Selecione o mês", list(meses.keys()), format_func=lambda x: meses[x])
        ano_especifico = st.selectbox("Selecione o ano", [2020, 2021, 2022, 2023, 2024])
        valores = [mes_especifico, ano_especifico]
    elif tipo_filtro == "ano":
        ano_especifico = st.selectbox("Selecione o ano", [2020, 2021, 2022, 2023, 2024])
        valores = [ano_especifico]
    elif tipo_filtro == "periodo":
        data_inicio = st.date_input("Data de início")
        data_fim = st.date_input("Data de término")
        if data_inicio and data_fim:
            valores = [data_inicio, data_fim]

    if valores:
        quantidade, emissao_total_formatado = calcular_emissoes(tipo_filtro, valores)
        st.metric("Quantidade", quantidade)
        st.metric("Valor Total", emissao_total_formatado)

if __name__ == "__main__":
    main()
