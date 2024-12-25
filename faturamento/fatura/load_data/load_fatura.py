import psycopg2 as psy
import pandas as pd
import streamlit as st
def load_fatura_from_sql():
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

    # columns = [
    #     'pesochegada', 'dataexportacao', 
    #     'dataatual', 'numeroconta', 
    #     'codtipoenvio', 'usuarioalt', 
    #     'numeropedido', 'numeropostagem', 
    #     'datapostagem', 'historico', 
    #     'historico1', 'historico2', 
    #     'usuarioins', 'codmercadoria', 
    #     'codcidadedestino', 'obs1', 
    #     'obsenvio', 'detcanc', 
    #     'precotonempresa', 'chavepix', 
    #     'parcelacopia', 'checklist', 
    #     'atualizadaadiantamento', 'codcidadeorigem'
    # ]
    # df_fatura = df_fatura.drop(columns=columns, errors='ignore')

    return df_fatura
