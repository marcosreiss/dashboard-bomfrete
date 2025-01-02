import psycopg2 as psy
import pandas as pd
import streamlit as st

def load_teste_from_sql():

    # query = "SELECT data, codcliente, valorclassificacao, freteempresa, fretemotorista, cancelado, pesosaida, pesochegada FROM conhecimento"

    query = "SELECT numeropedido, codfilial, codcliente, codveiculo,pesosaida, codmotorista, data,freteempresa, fretemotorista, adiantamentomotorista, especiemercadoria, valorpedagio, valorfretefiscal, codunidadeembarque, codcidadeorigem, codcidadedestino, cancelado, dataviagemmotorista FROM conhecimento "

    with psy.connect(
            host='satbomfrete.ddns.net',
            port='5409',
            user='eurico',
            password='SAT1234',
            database='bomfrete'
        ) as connection:
            df_fatura = pd.read_sql_query(query, connection)

    return df_fatura
