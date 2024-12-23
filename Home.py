import psycopg2 as psy
import pandas as pd
import streamlit as st

# def carregar_dados():
#     """Carrega os dados do banco de dados e os armazena no estado da sessão."""
#     if 'df_fatura' not in st.session_state:
#         query = "SELECT * FROM ordemcar"

#         with psy.connect(
#             host='satbomfrete.ddns.net',
#             port='5409',
#             user='eurico',
#             password='SAT1234',
#             database='bomfrete'
#         ) as connection:
#             st.session_state.df_fatura = pd.read_sql_query(query, connection)

#         st.session_state.df_fatura.dropna(how='all', axis=1, inplace=True)
        # st.session_state.df_fatura = st.session_state.df_fatura.drop(columns=[
        #     'codordemcar', 'numero', 'codfilial', 'codcliente', 'codremetente', 'coddestinatario', 'numeropedido',
        #     'data', 'dataatual', 'datadigitacao', 'codcidadeorigem', 'codcidadedestino', 'codcoleta', 'codentrega',
        #     'codveiculo', 'codmotorista', 'codmercadoria', 'usuarioins', 'usuarioalt', 'pesosaida', 'codunidadeembarque',
        #     'precotonmotorista', 'obs', 'obs1', 'obs2', 'obs3', 'obs4', 'quantmercadoria', 'especiemercadoria', 'tipo',
        #     'numeroviagem', 'codgerrisco', 'codconsignatario', 'cancelado', 'datacanc', 'usuariocanc', 'codrota',
        #     'listacoddestinatario', 'pedidofrete', 'pedidotransf', 'pedidocliente2', 'codespeciemerc', 'kmini', 'emitida',
        #     'codembarcador', 'impresso', 'motivocancelado', 'libgerriscoprop', 'tnfrete', 'contratopedido', 'ordemvenda',
        #     'protocolo', 'parceiro', 'pesocubado', 'status', 'datavalidade', 'previsaochegada', 'numautgerrisco',
        #     'dataenvgerrisco', 'codmotivocanc', 'codcontrato', 'codcoletasetor', 'codentregasetor', 'codordemcarant',
        #     'numeroseguro', 'expseguro', 'codgerriscoseg', 'arqxml', 'percadiantmotorista', 'precotonadtomot',
        #     'codfornecedoradiant', 'horainicarreg', 'horafimcarreg', 'statuslog', 'ordemcli', 'codcidadeorigem2',
        #     'codcidadedestino2', 'codcidadetrocanota', 'codcoleta2', 'codentrega2', 'precotonempresa', 'freteempresa',
        #     'fretemotorista', 'porccomissaoemb', 'vlcomissaoemb', 'codgerriscoped', 'codgerriscop', 'outrosdescontosmot2',
        #     'codfrete', 'checklistpagto', 'valorapolice', 'adtointegracao', 'percadtointegracao', 'lavagem', 'abastecimentointerno',
        #     'checklistrobosat'
        # ], errors='ignore')


def carregar_dados():
    """Carrega os dados da planilha CSV e os armazena no estado da sessão."""
    if 'df_teste' not in st.session_state:
        caminho_arquivo = 'tabelasCsv/ordemcar.csv'
        st.session_state.df_teste = pd.read_csv(caminho_arquivo)

def resumo_geral():
    """Exibe o resumo geral de eficiência das operações."""
    df = st.session_state.df_fatura

    total_embarques = len(df)
    entregas_no_prazo = df[df['status'] == 'Entregue no prazo'].shape[0] if 'status' in df.columns else 0
    percentual_no_prazo = (entregas_no_prazo / total_embarques * 100) if total_embarques > 0 else 0
    frota_utilizada = df['codveiculo'].nunique() if 'codveiculo' in df.columns else 0
    frota_total = 100  # Exemplo: total de veículos disponíveis
    taxa_utilizacao = (frota_utilizada / frota_total * 100) if frota_total > 0 else 0

    st.header("Resumo Geral")
    st.metric("Total de Embarques", total_embarques)
    st.metric("Percentual de Entregas no Prazo", f"{percentual_no_prazo:.2f}%")
    st.metric("Taxa de Utilização de Frota", f"{taxa_utilizacao:.2f}%")

def status_conhecimentos():
    """Exibe o status de conhecimentos e ordens."""
    df = st.session_state.df_fatura

    status_counts = df['status'].value_counts() if 'status' in df.columns else pd.Series()
    st.header("Status de Conhecimentos e Ordens")
    st.bar_chart(status_counts)

def custo_operacional():
    """Exibe a análise de custos operacionais."""
    df = st.session_state.df_fatura

    if 'fretemotorista' in df.columns and 'precotonmotorista' in df.columns:
        custo_total_motorista = df['fretemotorista'].sum() + df['precotonmotorista'].sum()
    else:
        custo_total_motorista = 0

    st.header("Custo Operacional")
    st.metric("Custo Total com Motoristas", f"R${custo_total_motorista:,.2f}")

def logistica_geografica():
    """Exibe a análise logística por unidade e região."""
    df = st.session_state.df_fatura

    if 'codcidadeorigem' in df.columns and 'codcidadedestino' in df.columns:
        regioes = df.groupby(['codcidadeorigem', 'codcidadedestino']).size().reset_index(name='Quantidade')
        st.header("Logística Geográfica")
        st.dataframe(regioes)

def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    carregar_dados()

    st.title("Dashboard de Logística Operacional")

    resumo_geral()
    status_conhecimentos()
    custo_operacional()
    logistica_geografica()

if __name__ == "__main__":
    main()
