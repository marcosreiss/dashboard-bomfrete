import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_teste_from_sql  # Tabela de conhecimento
from faturamento.fatura.load_data.load_contas import load_conta_from_sql
from faturamento.fatura.load_data.load_clientes import load_clientes_from_sql
import datetime

def bloco_kpi_estilizado(titulo, qtd, valor):
    """
    Cria um 'bloco' (tabela) estilizado para exibir:
    - Título (faixa verde escuro)
    - Cabeçalho: Qtd | Valor (faixa dourada)
    - Linha de dados: [qtd, valor] (fundo cinza)
    """
    table_html = f"""
    <div style="width: 300px; margin-bottom: 15px; border: 1px solid #CCCCCC; border-radius: 2px; overflow: hidden;">
        <!-- Título: fundo verde escuro -->
        <div style="background-color: #004C3F; color: #FFFFFF; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #A67C00; color: #FFFFFF; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FFFFFF;">Qtd</th>
                    <th style="padding: 5px;">Valor</th>
                </tr>
            </thead>
            <!-- Linha de dados: fundo cinza claro, texto preto -->
            <tbody>
                <tr style="background-color: #EEEEEE; text-align: center;">
                    <td style="padding: 8px; border-right: 1px solid #000000; color: #000000;">{qtd}</td>
                    <td style="padding: 8px; color: #000000;">{valor}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    # O ponto crucial é usar unsafe_allow_html=True
    st.markdown(table_html, unsafe_allow_html=True)


def bloco_kpi_estilizado_personalizado(titulo, qtd, valor, cabeca1, cabeca2):
    """
    Cria um 'bloco' (tabela) estilizado para exibir:
    - Título (faixa verde escuro)
    - Cabeçalho: Qtd | Valor (faixa dourada)
    - Linha de dados: [qtd, valor] (fundo cinza)
    """
    table_html = f"""
    <div style="width: 300px; margin-bottom: 15px; border: 1px solid #CCCCCC; border-radius: 2px; overflow: hidden;">
        <!-- Título: fundo verde escuro -->
        <div style="background-color: #004C3F; color: #FFFFFF; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #A67C00; color: #FFFFFF; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FFFFFF;">{cabeca1}</th>
                    <th style="padding: 5px;">{cabeca2}</th>
                </tr>
            </thead>
            <!-- Linha de dados: fundo cinza claro, texto preto -->
            <tbody>
                <tr style="background-color: #EEEEEE; text-align: center;">
                    <td style="padding: 8px; border-right: 1px solid #000000; color: #000000;">{qtd}</td>
                    <td style="padding: 8px; color: #000000;">{valor}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    # O ponto crucial é usar unsafe_allow_html=True
    st.markdown(table_html, unsafe_allow_html=True)


def bloco_kpi_estilizado_personalizado_tres(titulo, qtd, valor, cabeca1, cabeca2, cabeca3, valor1):
    """
    Cria um 'bloco' (tabela) estilizado para exibir:
    - Título (faixa verde escuro)
    - Cabeçalho: Qtd | Valor (faixa dourada)
    - Linha de dados: [qtd, valor] (fundo cinza)
    """
    table_html = f"""
    <div style="width: 300px; margin-bottom: 15px; border: 1px solid #CCCCCC; border-radius: 2px; overflow: hidden;">
        <!-- Título: fundo verde escuro -->
        <div style="background-color: #004C3F; color: #FFFFFF; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #A67C00; color: #FFFFFF; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FFFFFF;">{cabeca1}</th>
                    <th style="padding: 5px;">{cabeca2}</th>
                    <th style="padding: 5px;">{cabeca3}</th>
                </tr>
            </thead>
            <!-- Linha de dados: fundo cinza claro, texto preto -->
            <tbody>
                <tr style="background-color: #EEEEEE; text-align: center;">
                    <td style="padding: 8px; border-right: 1px solid #000000; color: #000000;">{qtd}</td>
                    <td style="padding: 8px; color: #000000;">{valor}</td>
                    <td style="padding: 8px; color: #000000;">{valor1}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    # O ponto crucial é usar unsafe_allow_html=True
    st.markdown(table_html, unsafe_allow_html=True)


def carregar_dados():
    """Carrega os dados de conhecimento e armazena no estado da sessão, sem usar ordemcar."""
    if 'df_conhecimento' not in st.session_state:
        df_conhecimento = load_teste_from_sql()
        st.session_state.df_conhecimento = df_conhecimento

def resumo_geral():
    """
    Exibe o resumo geral de eficiência das operações,
    agora usando blocos customizados (KPI).
    """
    df = st.session_state.df_conhecimento_filtrado

    total_embarques = len(df)
    
    # Exemplo de frota
    frota_utilizada = df['codveiculo'].nunique() if 'codveiculo' in df.columns else 0
    frota_total = 100  # Exemplo fixo

    
    bloco_kpi_estilizado_personalizado(
        titulo="Carros",
        qtd=total_embarques,
        valor=frota_utilizada,
        cabeca1="Fretes",
        cabeca2="Frota utilizada"

    )

def custo_operacional():
    """
    Exibe a análise de custos operacionais, incluindo freteMotorista e pedágio,
    agora no formato KPI estilizado.
    """
    df = st.session_state.df_conhecimento_filtrado

    # Gasto total com Frete Motorista
    custo_frete_motorista = (
        df['fretemotorista'].sum() if 'fretemotorista' in df.columns else 0
    )

    # Gasto total com Pedágio
    custo_pedagio = (
        df['valorpedagio'].sum() if 'valorpedagio' in df.columns else 0
    )
    
    custo_total = custo_frete_motorista + custo_pedagio

    bloco_kpi_estilizado_personalizado_tres(
        titulo="Custos",
        qtd=f"R${custo_frete_motorista:,.2f}",
        valor=f"R${custo_pedagio:,.2f}",
        valor1=f"R${custo_total:,.2f}",
        cabeca1="Motorista",
        cabeca2="Pedagio",
        cabeca3="Total"
    )

def pedidos_enviados():
    # Obtendo o DataFrame filtrado da sessão
    df = st.session_state.df_conhecimento_filtrado

    # Verifica se a coluna 'dataviagemmotorista' existe no DataFrame
    if 'dataviagemmotorista' in df.columns:
        # Total de pedidos (número de linhas no DataFrame)
        total_pedidos = len(df)

        # Total de enviados (não-nulos na coluna 'dataviagemmotorista')
        total_enviados = df['dataviagemmotorista'].notnull().sum()

        # Total de não enviados (valores nulos na coluna 'dataviagemmotorista')
        total_nao_enviados = df['dataviagemmotorista'].isnull().sum()
    else:
        # Caso a coluna não exista
        total_pedidos = 0
        total_enviados = 0
        total_nao_enviados = 0
        
    bloco_kpi_estilizado_personalizado_tres(
        titulo="Status pedidos",
        qtd=f"{total_pedidos}",
        valor=f"{total_enviados}",
        valor1=f"{total_nao_enviados}",
        cabeca1="Total",
        cabeca2="Enviados",
        cabeca3="Não Enviados"
    )

    

def logistica_geografica():
    """
    Exibe a análise logística por origem/destino usando o DataFrame filtrado.
    Aqui, se quiser, você pode manter o st.dataframe ou criar outro bloco, 
    mas normalmente é algo tabular mesmo.
    """
    df = st.session_state.df_conhecimento_filtrado

    st.header("Logística Geográfica - Conhecimentos (Filtrado)")
    if 'codcidadeorigem' in df.columns and 'codcidadedestino' in df.columns:
        regioes = (
            df.groupby(['codcidadeorigem', 'codcidadedestino'])
            .size()
            .reset_index(name='Quantidade')
        )
        # st.dataframe(regioes)
    else:
        st.info("Não há colunas 'codcidadeorigem' e/ou 'codcidadedestino' no df_conhecimento.")

def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    carregar_dados()

    st.title("Dashboard de Logística Operacional")

    tab1, tab2 = st.tabs(["Resumo Geral", "Detalhes por Caminhão"])
    
    with tab1:
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
            
            # Ajusta para não ultrapassar min/max
            min_data_date = min_data.date() if not pd.isnull(min_data) else hoje
            max_data_date = max_data.date() if not pd.isnull(max_data) else hoje
            default_start = max(min_data_date, uma_semana_atras)
            default_end = min(max_data_date, hoje)
            
            st.subheader("Filtro de Data")
            data_range = st.date_input(
                "Selecione o intervalo:",
                [default_start, default_end]
            )

            if len(data_range) == 2:
                start_date, end_date = data_range
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
        pedidos_enviados()



if __name__ == "__main__":
    if not st.session_state.get("logged_in", False):
        st.info('Please Login from the Home page and try again.')
        st.stop()
    else:
        main()
