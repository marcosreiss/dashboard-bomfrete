import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_teste_from_sql
from faturamento.fatura.load_data.load_contas import load_conta_from_sql
from faturamento.fatura.load_data.load_clientes import load_clientes_from_sql


from datetime import datetime, date, timedelta


def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_conhecimento' not in st.session_state:
        df_conhecimento = load_teste_from_sql()
        st.session_state.df_conhecimento = df_conhecimento

    if 'df_conta' not in st.session_state:
        df_conta = load_conta_from_sql()
        st.session_state.df_conta = df_conta

    if 'df_cliente' not in st.session_state:
        df_clientes = load_clientes_from_sql()
        st.session_state.df_clientes = df_clientes
    


def formatar_moeda_manual(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def trocadot(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
    met1, met2 = st.columns(2)
    with col1:
        st.metric("Quantidade Total", quantidade)
    with met1:
        st.metric("Valor Total", f"R${emissao_total:,.2f}")
    with col2:
        st.metric("Quantidade Válidas", quantidade_validas)
    with met2:    
        st.metric("Valor Válidas", f"R${freteempresa_validas:,.2f}")
    with col3:
        st.metric("Cancelados", f"{taxa_cancelamento}")
        # st.metric("Valor Canceladas", f"R${freteempresa_canceladas:,.2f}")


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

def calcular_metricas_caminhoes(df):
    """
    Calcula métricas relacionadas aos caminhões
    """
    try:
        # Contar número único de caminhões
        total_caminhoes = int(df['codveiculo'].nunique())
        
        # Verificar se a coluna existe
        if 'pesosaida' not in df.columns:
            print("Coluna 'pesosaida' não encontrada no DataFrame")
            return 0, 0.0
            
        # Pegar a série de pesosaida
        # Pegar a série de pesosaida
        serie_peso = df['pesosaida']

        # Converter para numérico, tratando erros e verificando o tipo
        serie_peso = pd.to_numeric(serie_peso, errors='coerce')
        if serie_peso.dtype != 'float64':
            print("A série 'pesosaida' não é do tipo numérico.")
            # Tentar converter novamente ou realizar outras ações

        # Remover valores NaN (opcional)
        serie_peso = serie_peso.dropna()

        # Calcular o total
        peso_total = serie_peso.sum()

        # Converter para toneladas
        peso_em_toneladas = peso_total / 1000
        
        # Mostrar registros com problemas
        valores_nao_numericos = serie_peso.isna()
        if valores_nao_numericos.any():
            print("\nRegistros com valores não numéricos:")
            print(df.loc[valores_nao_numericos, 'pesosaida'])
        
        return total_caminhoes, peso_em_toneladas
        
    except Exception as e:
        print(f"Erro ao calcular métricas: {str(e)}")
        return 0, 0.0
    


def mostrar_detalhes_pedidos_cliente(df_filtrado, clientes_selecionados_codigos):
    """Exibe detalhes dos pedidos como 'cards' + expander para detalhes."""
    
    df_cliente_pedidos = df_filtrado[df_filtrado['codcliente'].isin(clientes_selecionados_codigos)]
    
    if df_cliente_pedidos.empty:
        st.warning("Nenhum pedido encontrado para os clientes selecionados.")
        return
    
    
    
    st.subheader("Detalhes dos Pedidos por Cliente")

    # Renomear colunas para nomes mais legíveis (opcional)
    df_cliente_pedidos_renomeado = df_cliente_pedidos.rename(columns={
        'numeropedido': 'Número do Pedido',
        'codfilial': 'Filial',
        'codcliente': 'Código do Cliente',
        'especiemercadoria': 'Mercadoria',
        'data': 'Data',
        'codveiculo': 'Veículo',
        'freteempresa': 'Frete Empresa',
        'fretemotorista': 'Frete Motorista',
        'valorfretefiscal': 'Valor do Frete Fiscal',
        'valorpedagio': 'Valor do Pedágio',
        'cancelado': 'Cancelado',
        'codunidadeembarque': 'Código da Unidade de Embarque'
    })

    st.dataframe(df_cliente_pedidos_renomeado)

    # # Formata a coluna 'Data' como dd/mm/yyyy
    # df_cliente_pedidos_renomeado['Data'] = pd.to_datetime(
    #     df_cliente_pedidos_renomeado['Data']
    # ).dt.strftime('%d/%m/%Y')

    # # CSS para “cards”
    # st.markdown(
    #     """
    #     <style>
    #     .cards-container {
    #         display: flex;
    #         flex-wrap: wrap;
    #         justify-content: flex-start;
    #         gap: 10px;
    #     }
    #     .card {
    #         background-color: #2980B9; 
    #         color: white;
    #         border-radius: 8px;
    #         box-shadow: 1px 1px 5px rgba(0,0,0,0.2);
    #         padding: 16px;
    #         max-width: 450px;
    #         flex: 1 1 250px;
    #         margin-bottom: 10px;
    #     }
    #     .card:hover {
    #         /* Efeito suave ao passar o mouse */
    #         transform: scale(1.02);
    #         transition: transform 0.2s ease-in-out;
    #     }
    #     </style>
        
    #     <div class="cards-container">
    #     """,
    #     unsafe_allow_html=True
    # )

    # # Loop pelas linhas do DataFrame para gerar um card por pedido
    # for idx, row in df_cliente_pedidos_renomeado.iterrows():
    #     numero_pedido = row['Número do Pedido']
    #     data_pedido = row['Data']
    #     cod_cliente = row['Código do Cliente']
        
    #     # Campos detalhados
    #     veiculo = row['Veículo']
    #     mercadoria = row['Mercadoria']
    #     valor = row['Frete Empresa']
    #     pedagio = row['Valor do Pedágio']
    #     unidEmb = row['Código da Unidade de Embarque']
    #     freteMot = row['Frete Motorista']
        
    #     # Monta o HTML básico do cartão
    #     st.markdown(
    #         f"""
    #         <div class="card">
    #             <!-- Info principal -->
    #             <p>
    #               <strong>Nº Pedido:</strong> {numero_pedido} <br/>
    #               <strong>Data:</strong> {data_pedido} <br/>
    #               <strong>Cód Cliente:</strong> {cod_cliente}
    #             </p>
    #         """,
    #         unsafe_allow_html=True
    #     )
        
    #     # Agora, dentro do mesmo card, usamos o st.expander para os detalhes
    #     with st.expander("Ver detalhes", expanded=False):
    #         st.write(f"**Veículo:** {veiculo}")
    #         st.write(f"**Mercadoria:** {mercadoria}")
    #         st.write(f"**Valor:** {valor}")
    #         st.write(f"**Pedágio:** {pedagio}")
    #         st.write(f"**Unidade Emb.:** {unidEmb}")
    #         st.write(f"**Valor Motorista:** {freteMot}")
        
    #     # Fechamos a div do card
    #     st.markdown("</div>", unsafe_allow_html=True)
    
    # # Fechamos o container
    # st.markdown("</div>", unsafe_allow_html=True)



def exibir_metricas_caminhoes(total_caminhoes, peso_total):
    """
    Exibe as métricas dos caminhões usando cards do Streamlit
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Total de Caminhões",
            value=str(total_caminhoes)
        )
    
    with col2:
        st.metric(
            label="Peso Total Carregado (t)",
            value=trocadot(peso_total)
        )
def main():
    """Ponto de entrada principal do aplicativo Streamlit."""
    load_data()

    # Filtro de Intervalo de Tempo

    tab1, tab2, tab3 = st.tabs(["Resumo Geral", "Detalhes por Cliente", "Detalhes por Caminhão"])
    
    with tab1:
        st.header("Filtros")
        col1, col2 = st.columns(2)

        # Filtro de intervalo de tempo
        with col1:
            hoje = datetime.now()
            uma_semana_atras = hoje - timedelta(days=7)

            datas = st.date_input(
                "Selecione o intervalo de tempo",
                value=[uma_semana_atras, hoje],
                min_value=pd.to_datetime("2010-01-01"),
                max_value=pd.to_datetime("2050-12-31")
            )

            if len(datas) == 2:
                data_inicio = pd.Timestamp(datas[0]).replace(hour=0, minute=0, second=0)
                data_fim = pd.Timestamp(datas[1]).replace(hour=23, minute=59, second=59)
            else:
                st.warning("Selecione um intervalo de datas válido.")
                return

        df_conhecimento = st.session_state.df_conhecimento   
        df_filtrado = df_conhecimento.copy()
        df_filtrado = df_filtrado[
            (df_filtrado['data'] >= data_inicio) &
            (df_filtrado['data'] <= data_fim) ]

        # Filtro por codfilial
        with col2:
            
            lista_filiais = sorted(df_filtrado['codunidadeembarque'].dropna().unique())

            lista_opcoes = ["Todos"] + lista_filiais

            unidades_selecionadas = st.multiselect(
                "Selecione a(s) unidade(s) de embarque:",
                options=lista_opcoes,
                default=["Todos"]
            )

            if "Todos" in unidades_selecionadas:
                undidadeEmbarque = lista_filiais
            else:
                undidadeEmbarque = unidades_selecionadas


        # Converter a coluna 'data' para datetime
        df_filtrado['data'] = pd.to_datetime(df_filtrado['data'], errors='coerce')

        # Remover linhas com datas inválidas
        df_filtrado = df_filtrado.dropna(subset=['data'])

        # Aplicar filtros
        df_filtrado = df_filtrado[
            (df_filtrado['codunidadeembarque'].isin(undidadeEmbarque))
        ]

        if not df_filtrado.empty:
            calcular_kpis(df_filtrado)
        else:
            st.warning("Nenhum registro de fatura encontrado para os filtros selecionados.")

        # Calcular e exibir parcelas em aberto (adiantamento e saldo)
        df_conta = st.session_state.df_conta.copy()

        

        df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')

        print(df_conta.columns)

        df_filtrado_conta = df_conta[(df_conta['datavencimento'] >= data_inicio) &
            (df_conta['datavencimento'] <= data_fim) ]

        df_adiantamento, qtd_adiantamento, total_adiantamento, \
        df_saldo, qtd_saldo, total_saldo = calcular_parcelas_em_aberto(df_filtrado_conta)

        if qtd_adiantamento > 0 or qtd_saldo > 0:
            exibir_parcelas_em_aberto(df_adiantamento, qtd_adiantamento, total_adiantamento,
                                    df_saldo, qtd_saldo, total_saldo)
        else:
            st.info("Nenhuma parcela em aberto encontrada.")

        if not df_filtrado.empty:
            total_caminhoes, peso_total = calcular_metricas_caminhoes(df_filtrado)
            st.subheader("Métricas de Caminhões")
            exibir_metricas_caminhoes(total_caminhoes, peso_total)

    with tab2:
        # Carregar a lista de clientes
        df_clientes = st.session_state.df_clientes

        # Filtrar os pedidos mais recentes
        df_filtrado['data'] = pd.to_datetime(df_filtrado['data'])
        pedido_mais_recente = df_filtrado.loc[df_filtrado['data'].idxmax()]  # Encontrar o pedido mais recente

        # Obter o nome do cliente relacionado ao pedido mais recente
        codcliente_mais_recente = pedido_mais_recente['codcliente']
        cliente_mais_recente = df_clientes[df_clientes['codcliente'] == codcliente_mais_recente]['nome'].values[0]

        # Criar o dicionário, associando o nome do cliente ao código
        df_merged = pd.merge(df_clientes, df_filtrado, on='codcliente', how='right')
        map_nome_codigo = dict(zip(df_merged['nome'], df_merged['codcliente']))

        # Adicionar a opção "Todos" no início da lista
        lista_opcoes = ["Todos"] + list(map_nome_codigo.keys())

        # Criar o multiselect com a opção "Todos", com o cliente mais recente pré-selecionado
        clientes_selecionados = st.multiselect(
            "Selecione os clientes:",
            options=lista_opcoes,
            default=[cliente_mais_recente]  # Selecionar automaticamente o cliente com o pedido mais recente
        )

        # Obter os códigos dos clientes selecionados
        clientes_selecionados_codigos = [map_nome_codigo[nome] for nome in clientes_selecionados if nome != "Todos"]

        # Filtrar dados para os clientes selecionados
        if "Todos" in clientes_selecionados:
            df_filtrado_cliente = df_filtrado[
                (df_filtrado['data'] >= data_inicio) &
                (df_filtrado['data'] <= data_fim)
            ]
        else:
            df_filtrado_cliente = df_filtrado[
                (df_filtrado['data'] >= data_inicio) &
                (df_filtrado['data'] <= data_fim) &
                (df_filtrado['codcliente'].isin(clientes_selecionados_codigos))
            ]

        if not df_filtrado_cliente.empty:
            calcular_kpis(df_filtrado_cliente)
            mostrar_detalhes_pedidos_cliente(df_filtrado_cliente, clientes_selecionados_codigos)
            
            total_caminhoes, peso_total = calcular_metricas_caminhoes(df_filtrado_cliente)
            st.subheader("Métricas de Caminhões")
            exibir_metricas_caminhoes(total_caminhoes, peso_total)

        else:
            st.warning("Nenhum registro de fatura encontrado para os filtros selecionados.")






        


if __name__ == "__main__":
    main()
