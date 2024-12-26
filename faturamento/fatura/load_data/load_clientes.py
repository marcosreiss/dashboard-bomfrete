import psycopg2 as psy
import pandas as pd
import streamlit as st

def load_clientes_from_sql():

    # query = "SELECT data, codcliente, valorclassificacao, freteempresa, fretemotorista, cancelado, pesosaida, pesochegada FROM conhecimento"

    query = f"SELECT codcliente,nome FROM cliente "

    with psy.connect(
            host='satbomfrete.ddns.net',
            port='5409',
            user='eurico',
            password='SAT1234',
            database='bomfrete'
        ) as connection:
            df_clientes = pd.read_sql_query(query, connection)

    return df_clientes
