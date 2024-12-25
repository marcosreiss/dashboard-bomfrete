import psycopg2 as psy
import pandas as pd
import streamlit as st
def load_conta_from_sql():
    query = "SELECT * FROM duplicatareceber"

    with psy.connect(
            host='satbomfrete.ddns.net',
            port='5409',
            user='eurico',
            password='SAT1234',
            database='bomfrete'
        ) as connection:
            df_conta = pd.read_sql_query(query, connection)

    df_conta.dropna(how='all', axis=1, inplace=True)

    return df_conta
