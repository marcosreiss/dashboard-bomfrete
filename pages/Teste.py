import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_teste_from_sql
from faturamento.fatura.load_data.load_contas import load_conta_from_sql


from datetime import datetime, date, timedelta


def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_conhecimento' not in st.session_state:
        df_conhecimento = load_teste_from_sql()
        st.session_state.df_conhecimento = df_conhecimento

    if 'df_conta' not in st.session_state:
        df_conta = load_conta_from_sql()
        st.session_state.df_conta = df_conta
    



def calcular_kpis(df_filtrado):
    """Calcula KPIs e indicadores chave."""
    # Quantidade total
    quantidade = df_filtrado.shape[0]

    # Valor total
    df_filtrado['freteempresa'] = df_filtrado['freteempresa'].fillna(0)
    emissao_total = df_filtrado['freteempresa'].sum()

    # Emissões válidas
    df_validas = df_filtrado[df_filtrado["cancelado"] == 'N']
    quantidade_validas = df_validas.shape[0]
    freteempresa_validas = df_validas['freteempresa'].sum()

    # Emissões canceladas
    df_canceladas = df_filtrado[df_filtrado["cancelado"] == 'S']
    quantidade_canceladas = df_canceladas.shape[0]
    freteempresa_canceladas = df_canceladas['freteempresa'].sum()

    # Taxa de cancelamento
    taxa_cancelamento = quantidade_canceladas

    # Exibição dos KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quantidade Total", quantidade)
        st.metric("Valor Total", f"R${emissao_total:,.2f}")
    with col2:
        st.metric("Quantidade Válidas", quantidade_validas)
        st.metric("Valor Válidas", f"R${freteempresa_validas:,.2f}")
    with col3:
        st.metric("Taxa de Cancelamento", f"{taxa_cancelamento:.2f}%")
        st.metric("Valor Canceladas", f"R${freteempresa_canceladas:,.2f}")


def calcular_parcelas_em_aberto(df_conta):
    """Filtra e separa as parcelas em aberto por adiantamento e saldo."""
    # Certifique-se de que as datas estão no formato datetime
    df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')
    df_conta['datapagamento'] = pd.to_datetime(df_conta['datapagamento'], errors='coerce')

    # Data atual
    hoje = pd.Timestamp.now()

    # Identificar adiantamentos
    df_adiantamento = df_conta[
        (df_conta['valorpagamento'] > 0) &  # Há um pagamento parcial
        (df_conta['valorpagamento'] < df_conta['valorvencimento']) |  # Pagamento menor que o total
        (df_conta['datapagamento'] < df_conta['datavencimento'])  # Pagamento antes do vencimento
    ]

    # Identificar saldos
    df_saldo = df_conta[
        (df_conta['datavencimento'] < hoje) &  # Já venceu
        ((df_conta['valorpagamento'].isna()) | (df_conta['valorpagamento'] == 0))  # Não pago
    ]

    # Totalizadores
    total_adiantamento = df_adiantamento['valorvencimento'].sum()
    quantidade_adiantamento = df_adiantamento.shape[0]

    total_saldo = df_saldo['valorvencimento'].sum()
    quantidade_saldo = df_saldo.shape[0]

    return df_adiantamento, quantidade_adiantamento, total_adiantamento, df_saldo, quantidade_saldo, total_saldo


def exibir_parcelas_em_aberto(df_adiantamento, qtd_adiantamento, total_adiantamento,
                              df_saldo, qtd_saldo, total_saldo):
    """Exibe as informações de parcelas em aberto no dashboard, separadas por adiantamento e saldo."""
    # Indicadores de Adiantamento
    st.markdown("### Adiantamentos")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Quantidade de Adiantamentos", qtd_adiantamento)
    with col2:
        st.metric("Valor Total de Adiantamentos", f"R${total_adiantamento:,.2f}")

    # Indicadores de Saldo
    st.markdown("### Saldos")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Quantidade de Saldos", qtd_saldo)
    with col4:
        st.metric("Valor Total de Saldos", f"R${total_saldo:,.2f}")


def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    load_data()

    # Filtro de Intervalo de Tempo
    st.header("Filtros")
    col1, col2 = st.columns(2)

    # Filtro de intervalo de tempo
    with col1:
    # Calcular o intervalo de datas padrão (uma semana antes da data atual)
        hoje = datetime.now()
        uma_semana_atras = hoje - timedelta(days=7)

        # Configurar o campo de seleção de datas
        datas = st.date_input(
            "Selecione o intervalo de tempo",
            value=[uma_semana_atras, hoje],  # Intervalo padrão: de uma semana atrás até hoje
            min_value=pd.to_datetime("2010-01-01"),
            max_value=pd.to_datetime("2050-12-31")
        )

        if len(datas) == 2:
            # Ajustar as datas para o início e fim do dia
            data_inicio = pd.Timestamp(datas[0]).replace(hour=0, minute=0, second=0)
            data_fim = pd.Timestamp(datas[1]).replace(hour=23, minute=59, second=59)
        else:
            st.warning("Selecione um intervalo de datas válido.")
            return

    # Filtro por codfilial
    with col2:
        df_conhecimento = st.session_state.df_conhecimento
        lista_filiais = sorted(df_conhecimento['codunidadeembarque'].dropna().unique())  # Lista de filiais únicas

        # Adicionar a opção "Todos" no início da lista
        lista_opcoes = ["Todos"] + lista_filiais

        # Criar o multiselect com a opção "Todos"
        unidades_selecionadas = st.multiselect(
            "Selecione a(s) unidade(s) de embarque:",
            options=lista_opcoes,
            default=["Todos"]  # Por padrão, "Todos" é selecionado
        )

        # Verificar se "Todos" foi selecionado
        if "Todos" in unidades_selecionadas:
            undidadeEmbarque = lista_filiais  # Seleciona todas as unidades
        else:
            undidadeEmbarque = unidades_selecionadas  # Seleciona apenas as unidades específicas




    # Filtrar dados com base nos filtros selecionados
    df_filtrado = df_conhecimento.copy()

    # Converter a coluna 'data' para datetime
    df_filtrado['data'] = pd.to_datetime(df_filtrado['data'], errors='coerce')

    # Remover linhas com datas inválidas
    df_filtrado = df_filtrado.dropna(subset=['data'])

    # Aplicar filtros
    df_filtrado = df_filtrado[
        (df_filtrado['data'] >= data_inicio) &
        (df_filtrado['data'] <= data_fim) &
        (df_filtrado['codunidadeembarque'].isin(undidadeEmbarque))
    ]

    if not df_filtrado.empty:
        calcular_kpis(df_filtrado)

    else:
        st.warning("Nenhum registro de fatura encontrado para os filtros selecionados.")

    # Calcular e exibir parcelas em aberto (adiantamento e saldo)
    df_conta = st.session_state.df_conta.copy()

    df_adiantamento, qtd_adiantamento, total_adiantamento, \
    df_saldo, qtd_saldo, total_saldo = calcular_parcelas_em_aberto(df_conta)

    if qtd_adiantamento > 0 or qtd_saldo > 0:
        exibir_parcelas_em_aberto(df_adiantamento, qtd_adiantamento, total_adiantamento,
                                  df_saldo, qtd_saldo, total_saldo)
    else:
        st.info("Nenhuma parcela em aberto encontrada.")

if __name__ == "__main__":
    main()
