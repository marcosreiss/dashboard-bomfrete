import pandas as pd
import streamlit as st
from faturamento.fatura.load_data.load_fatura import load_fatura_from_sql
from faturamento.fatura.load_data.load_contas import load_conta_from_sql


def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_fatura' not in st.session_state:
        df_fatura = load_fatura_from_sql()
        st.session_state.df_fatura = df_fatura

    if 'df_conta' not in st.session_state:
        df_conta = load_conta_from_sql()
        st.session_state.df_conta = df_conta


def calcular_kpis(df_filtrado):
    """Calcula KPIs e indicadores chave."""
    # Quantidade total
    quantidade = df_filtrado.shape[0]

    # Valor total
    df_filtrado['valor'] = df_filtrado['valor'].fillna(0)
    emissao_total = df_filtrado['valor'].sum()

    # Emissões válidas
    df_validas = df_filtrado[df_filtrado["status"] == 'N']
    quantidade_validas = df_validas.shape[0]
    valor_validas = df_validas['valor'].sum()

    # Emissões canceladas
    df_canceladas = df_filtrado[df_filtrado["status"] == 'C']
    quantidade_canceladas = df_canceladas.shape[0]
    valor_canceladas = df_canceladas['valor'].sum()

    # Taxa de cancelamento
    taxa_cancelamento = (quantidade_canceladas / quantidade) * 100 if quantidade > 0 else 0

    # Exibição dos KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quantidade Total", quantidade)
        st.metric("Valor Total", f"R${emissao_total:,.2f}")
    with col2:
        st.metric("Quantidade Válidas", quantidade_validas)
        st.metric("Valor Válidas", f"R${valor_validas:,.2f}")
    with col3:
        st.metric("Taxa de Cancelamento", f"{taxa_cancelamento:.2f}%")
        st.metric("Valor Canceladas", f"R${valor_canceladas:,.2f}")


def calcular_parcelas_em_aberto(df_conta):
    """Filtra e calcula as parcelas em aberto."""
    # Certifique-se de que as datas estão no formato datetime
    df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')
    df_conta['datapagamento'] = pd.to_datetime(df_conta['datapagamento'], errors='coerce')

    # Data atual
    hoje = pd.Timestamp.now()

    # Filtrar parcelas em aberto
    df_em_aberto = df_conta[
        (df_conta['datavencimento'] < hoje) &  # Já venceu
        ((df_conta['valorpagamento'].isna()) | (df_conta['valorpagamento'] == 0))  # Não pago
    ]

    # Calcular total de parcelas em aberto
    total_em_aberto = df_em_aberto['valorvencimento'].sum()
    quantidade_em_aberto = df_em_aberto.shape[0]

    return df_em_aberto, quantidade_em_aberto, total_em_aberto


def exibir_parcelas_em_aberto(df_em_aberto, quantidade, total):
    """Exibe as informações de parcelas em aberto no dashboard."""
    st.subheader("Parcelas em Aberto")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Quantidade de Parcelas em Aberto", quantidade)
    with col2:
        st.metric("Valor Total de Parcelas em Aberto", f"R${total:,.2f}")

    # Exibir detalhes das parcelas em aberto em uma tabela
    st.dataframe(df_em_aberto[['codfatura', 'parcela', 'datavencimento', 'valorvencimento']])


def plot_distribuicao_temporal(df_filtrado):
    """Plota gráfico de barras para distribuição temporal."""
    df_temporal = df_filtrado.groupby(df_filtrado['data'].dt.date)['valor'].sum().reset_index()
    df_temporal.columns = ['Data', 'Valor']

    st.bar_chart(df_temporal.set_index('Data'))


def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    load_data()

    st.title("Dashboard Financeiro - Bomfrete")
    st.subheader("Indicadores e Análises")

    st.header("Filtro de Intervalo de Tempo")
    col1, col2 = st.columns(2)

    with col1:
        datas = st.date_input(
            "Selecione o intervalo de tempo",
            value=[pd.to_datetime("2024-12-01"), pd.to_datetime("2024-12-31")],
            min_value=pd.to_datetime("2010-01-01"),
            max_value=pd.to_datetime("2050-12-31")
        )

    if len(datas) == 2:
        data_inicio, data_fim = pd.to_datetime(datas[0]), pd.to_datetime(datas[1])
    else:
        st.warning("Selecione um intervalo de datas válido.")
        return

    # Filtrar e calcular KPIs para faturas
    df_filtrado = st.session_state.df_fatura.copy()
    df_filtrado['data'] = pd.to_datetime(df_filtrado['data'], errors='coerce')
    df_filtrado = df_filtrado[(df_filtrado['data'] >= data_inicio) & (df_filtrado['data'] <= data_fim)]

    if not df_filtrado.empty:
        calcular_kpis(df_filtrado)

        st.subheader("Distribuição Temporal")
        plot_distribuicao_temporal(df_filtrado)
    else:
        st.warning("Nenhum registro de fatura encontrado para o intervalo selecionado.")

    # Calcular e exibir parcelas em aberto
    df_conta = st.session_state.df_conta.copy()
    df_em_aberto, quantidade_em_aberto, total_em_aberto = calcular_parcelas_em_aberto(df_conta)

    if quantidade_em_aberto > 0:
        exibir_parcelas_em_aberto(df_em_aberto, quantidade_em_aberto, total_em_aberto)
    else:
        st.info("Nenhuma parcela em aberto encontrada.")


if __name__ == "__main__":
    main()
