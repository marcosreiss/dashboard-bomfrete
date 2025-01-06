import psycopg2 as psy
import pandas as pd
import streamlit as st





@st.cache_resource
def load_fatura_from_sql():
    # query = """
    # SELECT f.*, cp.codcondicao, cp.numeroparcelas
    # FROM fatura f
    # LEFT JOIN condpag cp
    # ON f.codcondicao = cp.codcondicao
    # """

    query = "SELECT * FROM fatura"

    with psy.connect(
            host='satbomfrete.ddns.net',
            port='5409',
            user='eurico',
            password='SAT1234',
            database='bomfrete'
        ) as connection:
            df_fatura = pd.read_sql_query(query, connection)

    df_fatura.dropna(how='all', axis=1, inplace=True)

    # df_fatura.to_excel("fatura.xlsx")

    return df_fatura
