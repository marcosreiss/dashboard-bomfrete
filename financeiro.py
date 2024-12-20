import psycopg2 as psy
import pandas as pd
import streamlit as st

# Consulta e armazenamento inicial do DataFrame no estado
if 'df_fatura' not in st.session_state:
    query = "SELECT * FROM fatura"

    with psy.connect(
        host='satbomfrete.ddns.net',
        port='5409',
        user='eurico',
        password='SAT1234',
        database='bomfrete'
    ) as connection:
        st.session_state.df_fatura = pd.read_sql_query(query, connection)

    st.session_state.df_fatura.dropna(how='all', axis=1, inplace=True)
    st.session_state.df_fatura = st.session_state.df_fatura.drop(columns=[
        'pesochegada', 'dataexportacao', 'dataatual', 'numeroconta', 'codtipoenvio', 'usuarioalt', 'numeropedido',
        'numeropostagem', 'datapostagem', 'historico', 'historico1', 'historico2', 'usuarioins', 'codmercadoria', 'codcidadedestino',
        'obs1', 'obsenvio', 'detcanc', 'precotonempresa', 'chavepix', 'parcelacopia', 'checklist', 'atualizadaadiantamento', 'codcidadeorigem'
    ], errors='ignore')

# Função para calcular quantidade e valor baseado no filtro escolhido
def calcular_emissoes(tipo_filtro, valores):
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
        df_filtrado = df_fatura[(df_fatura['data'] >= pd.to_datetime(data_inicio)) & (df_fatura['data'] <= pd.to_datetime(data_fim))]
    else:
        st.error("Tipo de filtro inválido!")
        return 0, "R$0,00"

    # Calcula quantidade e emissão total
    quantidade = df_filtrado.shape[0]
    emissao_total = df_filtrado['valor'].sum()
    emissao_total_formatado = f"R${emissao_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    return quantidade, emissao_total_formatado

# Função para calcular emissões válidas
def calcular_emissoes_validas(tipo_filtro, valores):
    df_fatura = st.session_state.df_fatura

    if tipo_filtro == "dia":
        data_especifica = valores[0]
        df_filtrado = df_fatura[(df_fatura['data'] == pd.to_datetime(data_especifica)) & (df_fatura['status'] == 'N')]
    elif tipo_filtro == "mes":
        mes_especifico, ano_especifico = valores
        df_filtrado = df_fatura[(df_fatura['data'].dt.month == mes_especifico) &
                                (df_fatura['data'].dt.year == ano_especifico) &
                                (df_fatura['status'] == 'N')]
    elif tipo_filtro == "ano":
        ano_especifico = valores[0]
        df_filtrado = df_fatura[(df_fatura['data'].dt.year == ano_especifico) & (df_fatura['status'] == 'N')]
    elif tipo_filtro == "periodo":
        data_inicio, data_fim = valores
        df_filtrado = df_fatura[(df_fatura['data'] >= pd.to_datetime(data_inicio)) & 
                                (df_fatura['data'] <= pd.to_datetime(data_fim)) &
                                (df_fatura['status'] == 'N')]
    else:
        st.error("Tipo de filtro inválido!")
        return 0, "R$0,00"

    # Calcula quantidade e emissão total
    quantidade = df_filtrado.shape[0]
    emissao_total = df_filtrado['valor'].sum()
    emissao_total_formatado = f"R${emissao_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    return quantidade, emissao_total_formatado

# Interface do usuário no Streamlit
st.title("Bomfrete Financeiro")
st.subheader("Indicadores de emissão")

# Seleção do tipo de filtro
tipo_filtro = st.selectbox("Selecione o tipo de filtro", ["dia", "mes", "ano", "periodo"], format_func=lambda x: x.capitalize())

# Entrada de valores baseados no filtro escolhido
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

# Calcula os resultados com base no filtro
if valores:
    quantidade, emissao_total_formatado = calcular_emissoes(tipo_filtro, valores)
    quantidade_validas, emissao_validas_formatado = calcular_emissoes_validas(tipo_filtro, valores)

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Emissão Total")
        st.metric(label="Quantidade", value=quantidade)
        st.metric(label="Valor", value=emissao_total_formatado)

    with col2:
        st.write("### Emissão Válida")
        st.metric(label="Quantidade", value=quantidade_validas)
        st.metric(label="Valor", value=emissao_validas_formatado)
