import psycopg2 as psy
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st

# Função para tratar os dados XML
def parse_xml_column(xml_data):
    try:
        # Parse o XML
        namespaces = {'ns': 'http://www.portalfiscal.inf.br/cte'}  # Namespace do XML
        root = ET.fromstring(xml_data)

        # Dicionário para armazenar os dados extraídos
        data = {}

        # Informações gerais do CTe
        inf_cte = root.find('ns:infCte', namespaces)
        if inf_cte is not None:
            data['Id'] = inf_cte.attrib.get('Id', None)
            data['versao'] = inf_cte.attrib.get('versao', None)

            # Nó ide
            ide = inf_cte.find('ns:ide', namespaces)
            if ide is not None:
                data['cUF'] = ide.find('ns:cUF', namespaces).text if ide.find('ns:cUF', namespaces) else None
                data['cMunIni'] = ide.find('ns:cMunIni', namespaces).text if ide.find('ns:cMunIni', namespaces) else None
                data['xMunIni'] = ide.find('ns:xMunIni', namespaces).text if ide.find('ns:xMunIni', namespaces) else None
                data['cMunFim'] = ide.find('ns:cMunFim', namespaces).text if ide.find('ns:cMunFim', namespaces) else None
                data['xMunFim'] = ide.find('ns:xMunFim', namespaces).text if ide.find('ns:xMunFim', namespaces) else None

            # Nó emit
            emit = inf_cte.find('ns:emit', namespaces)
            if emit is not None:
                cnpj_node = emit.find('ns:CNPJ', namespaces)
                data['emit_CNPJ'] = cnpj_node.text if cnpj_node is not None else None

                nome_node = emit.find('ns:xNome', namespaces)
                data['emit_xNome'] = nome_node.text if nome_node is not None else None

        return data
    except ET.ParseError as e:
        return {"Erro": f"Erro ao parsear o XML: {str(e)}"}
    except Exception as e:
        return {"Erro": str(e)}

# Função para carregar e tratar dados do banco de dados
@st.cache_resource
def load_teste_from_sql():
    query = """
        SELECT 
            numeropedido, codcliente, codveiculo, pesosaida,
            codmotorista, data, freteempresa, fretemotorista, 
            adiantamentomotorista, especiemercadoria, valorpedagio, 
            valorfretefiscal, codunidadeembarque, codcidadeorigem, 
            codcidadedestino, cancelado, dataviagemmotorista, arqxmlass
        FROM conhecimento   
    """

    # Conexão com o banco de dados
    with psy.connect(
        host='satbomfrete.ddns.net',
        port='5409',
        user='eurico',
        password='SAT1234',
        database='bomfrete'
    ) as connection:
        df_fatura = pd.read_sql_query(query, connection)
    
    # Tratamento da coluna XML
    if 'arqxmlass' in df_fatura.columns:
        xml_data_processed = df_fatura['arqxmlass'].apply(parse_xml_column)
        xml_df = pd.DataFrame(list(xml_data_processed))
        df_fatura = pd.concat([df_fatura.drop(columns=['arqxmlass']), xml_df], axis=1)

    df_fatura.to_excel("conhecimento.xlsx")
    return df_fatura

# Para testar
if __name__ == "__main__":
    df = load_teste_from_sql()
    print(df.head())
