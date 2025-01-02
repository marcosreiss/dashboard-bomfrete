import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
from Teste.load_teste import load_teste_from_sql
from faturamento.fatura.load_data.load_contas import load_conta_from_sql
from faturamento.fatura.load_data.load_clientes import load_clientes_from_sql
from faturamento.fatura.load_data.load_fatura import load_fatura_from_sql
# from Login.autenticacao import entrar
import pymongo
from pymongo.errors import PyMongoError
# from streamlit import experimental_rerun

from datetime import datetime, date, timedelta




# Substitua <db_password> pela sua senha real
uri = "mongodb+srv://admin:admin@cluster0.s5hbe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def verificar_usuario_senha(usuario, senha):
    """
    Verifica se o usuário e senha existem no banco de dados MongoDB.
    Retorna uma tupla (True, role) se o usuário existe e (False, None) caso contrário.
    """
    try:
        client = pymongo.MongoClient(uri)
        db = client["meu_banco"]    # Troque para o seu BD
        usuarios = db["usuarios"]   # Troque para sua coleção

        resultado = usuarios.find_one({
            "usuario": usuario,
            "senha": senha
        })
        if resultado:
            # Se encontrou usuário, retorna True + a role
            return True, resultado.get("role")
        else:
            # Se não encontrou, retorna False + None
            return False, None
    
    except PyMongoError as e:
        st.error(f"Erro ao conectar no MongoDB: {e}")
        # Em caso de erro, também retorne (False, None)
        return False, None

def entrar():
    """
    Exibe os campos de login e retorna (autenticador_status, username, role).
    """
    # Garanta a existência dessas chaves no session_state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None

    st.title("Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        autenticado, role_encontrada = verificar_usuario_senha(usuario, senha)

        if autenticado:
            st.session_state["logged_in"] = True
            st.session_state['username'] = usuario
            st.session_state['role'] = role_encontrada
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.session_state["logged_in"] = False
            st.error("Usuário ou senha inválidos.")

    return st.session_state["logged_in"], st.session_state['username'], st.session_state['role']



def load_data():
    """Carrega os dados do banco de dados e os armazena no estado da sessão."""
    if 'df_conhecimento' not in st.session_state:
        df_conhecimento = load_teste_from_sql()
        # df_conhecimento =  pd.read_excel(
        #     r"C:\Users\jtchb\OneDrive\Área de Trabalho\Bom_Frete\dashboard-bomfrete\tabelaxlsx\conhecimento.xlsx"
        # )
        st.session_state.df_conhecimento = df_conhecimento

    if 'df_conta' not in st.session_state:
        df_conta = load_conta_from_sql()
        # df_conta = pd.read_excel(
        #     r"C:\Users\jtchb\OneDrive\Área de Trabalho\Bom_Frete\dashboard-bomfrete\tabelaxlsx\conta.xlsx"
        # )
        st.session_state.df_conta = df_conta

    if 'df_cliente' not in st.session_state:
        df_clientes = load_clientes_from_sql()
        # df_clientes = pd.read_excel(
        #     r"C:\Users\jtchb\OneDrive\Área de Trabalho\Bom_Frete\dashboard-bomfrete\tabelaxlsx\clientes.xlsx"
        # )
        st.session_state.df_clientes = df_clientes
        
    if 'df_fatura' not in st.session_state:
        df_fatura = load_fatura_from_sql()
        # df_fatura = pd.read_excel(
        #     r"C:\Users\jtchb\OneDrive\Área de Trabalho\Bom_Frete\dashboard-bomfrete\tabelaxlsx\fatura.xlsx"
        # )
        st.session_state.df_fatura = df_fatura


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

    # Taxa de cancelamento (exemplo)
    taxa_cancelamento = quantidade_canceladas
    
    # Formatação do valor em Reais
    valor_total_str = formatar_moeda_manual(emissao_total)  
    valor_validas_str = formatar_moeda_manual(freteempresa_validas)
    valor_canceladas_str = formatar_moeda_manual(freteempresa_canceladas)

    # Exibição dos KPIs em colunas com blocos customizados
    col1, col2, col3 = st.columns(3)

    with col1:
        bloco_kpi_estilizado(
            titulo="EMISSÃO TOTAL",
            qtd=quantidade,
            valor=valor_total_str
        )
    with col2:
        bloco_kpi_estilizado(
            titulo="EMISSÕES VÁLIDAS",
            qtd=quantidade_validas,
            valor=valor_validas_str
        )
    with col3:
        bloco_kpi_estilizado(
            titulo="CANCELADAS",
            qtd=taxa_cancelamento,
            valor=valor_canceladas_str
        )
def calcular_parcelas_em_aberto(df_conta):
    """Filtra e separa as parcelas em aberto por adiantamento, saldo e vencidos."""
    df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')
    df_conta['datapagamento'] = pd.to_datetime(df_conta['datapagamento'], errors='coerce')

    hoje = pd.Timestamp.now()

    # Adiantamentos (pagamentos parciais antes do vencimento)
    df_adiantamento = df_conta[
        (
            (df_conta['valorpagamento'] > 0) & 
            (df_conta['valorpagamento'] < df_conta['valorvencimento'])
        )
        |
        (
            df_conta['datapagamento'] < df_conta['datavencimento']
        )
    ]

    # Saldos em aberto (parcelas não pagas e vencidas)
    df_saldo = df_conta[
        (df_conta['datavencimento'] < hoje) & 
        (
            (df_conta['valorpagamento'].isna()) | 
            (df_conta['valorpagamento'] == 0)
        )
    ]

    # Vencidos (parcelas vencidas e ainda não pagas)
    df_vencidos = df_conta[
        (df_conta['datavencimento'] < hoje) &
        (
            (df_conta['valorpagamento'].isna()) |
            (df_conta['valorpagamento'] < df_conta['valorvencimento'])
        )
    ]

    # Totalizadores
    total_adiantamento = df_adiantamento['valorvencimento'].sum()
    quantidade_adiantamento = df_adiantamento.shape[0]

    total_saldo = df_saldo['valorvencimento'].sum()
    quantidade_saldo = df_saldo.shape[0]

    total_vencidos = df_vencidos['valorvencimento'].sum()
    quantidade_vencidos = df_vencidos.shape[0]

    return (
        df_adiantamento, quantidade_adiantamento, total_adiantamento,
        df_saldo, quantidade_saldo, total_saldo,
        df_vencidos, quantidade_vencidos, total_vencidos
    )



def exibir_parcelas_em_aberto(df_adiantamento, qtd_adiantamento, total_adiantamento,
                              df_saldo, qtd_saldo, total_saldo,
                              df_vencidos, qtd_vencidos, total_vencidos):
    """
    Exibe as informações de parcelas em aberto no dashboard,
    usando o mesmo estilo de bloco para Adiantamentos, Saldos e Vencidos.
    """

    st.markdown("### Parcelas em Aberto")

    # Mostra Adiantamentos, Saldos e Vencidos em três colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        bloco_kpi_estilizado(
            titulo="ADIANTAMENTOS",
            qtd=qtd_adiantamento,
            valor=f"R${trocadot(total_adiantamento)}"
        )
    with col2:
        bloco_kpi_estilizado(
            titulo="SALDOS",
            qtd=qtd_saldo,
            valor=f"R${trocadot(total_saldo)}"
        )
    with col3:
        bloco_kpi_estilizado(
            titulo="VENCIDOS",
            qtd=qtd_vencidos,
            valor=f"R${trocadot(total_vencidos)}"
        )



def calcular_metricas_caminhoes(df):
    """Calcula métricas relacionadas aos caminhões."""
    try:
        total_caminhoes = int(df['codveiculo'].nunique())
        
        if 'pesosaida' not in df.columns:
            print("Coluna 'pesosaida' não encontrada no DataFrame")
            return 0, 0.0

        serie_peso = pd.to_numeric(df['pesosaida'], errors='coerce')
        serie_peso = serie_peso.dropna()

        peso_total = serie_peso.sum()
        peso_em_toneladas = peso_total / 1000

        return total_caminhoes, peso_em_toneladas
        
    except Exception as e:
        print(f"Erro ao calcular métricas: {str(e)}")
        return 0, 0.0


def mostrar_detalhes_pedidos_cliente(df_filtrado, clientes_selecionados_codigos):
    """Exibe detalhes dos pedidos como tabela."""
    df_cliente_pedidos = df_filtrado[df_filtrado['codcliente'].isin(clientes_selecionados_codigos)]
    
    if df_cliente_pedidos.empty:
        st.warning("Nenhum pedido encontrado para os clientes selecionados.")
        return


    # Renomear colunas para nomes mais legíveis (opcional)
    df_renomeado = df_cliente_pedidos.rename(columns={
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

def exibir_metricas_faturas_por_cliente(clientes):
    """
    Exibe as métricas calculadas de faturas por cliente no dashboard.
    """
    st.markdown("### Métricas de Faturas por Cliente")

    metricas = calcular_metricas_faturas_por_cliente(clientes)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        bloco_kpi_estilizado(
            titulo="Pagas",
            qtd=metricas["pagas"][0],
            valor=f"R${trocadot(metricas['pagas'][1])}"
        )
    with col2:
        bloco_kpi_estilizado(
            titulo="Em Aberto",
            qtd=metricas["aberto"][0],
            valor=f"R${trocadot(metricas['aberto'][1])}"
        )
    with col3:
        bloco_kpi_estilizado(
            titulo="Vencidas",
            qtd=metricas["vencidas"][0],
            valor=f"R${trocadot(metricas['vencidas'][1])}"
        )
    with col4:
        bloco_kpi_estilizado(
            titulo="Adiantamento",
            qtd=metricas["adiantamento"][0],
            valor=f"R${trocadot(metricas['adiantamento'][1])}"
        )
    with col5:
        bloco_kpi_estilizado(
            titulo="Média Atraso (dias)",
            qtd="",
            valor=f"{metricas['media_atraso']:.1f} dias"
        )


def calcular_metricas_faturas_por_cliente(clientes_selecionados_codigos):
    """
    Calcula métricas de faturas por cliente, incluindo faturas pagas, em aberto, vencidas, e adiantamentos.
    """
    # Obter os DataFrames do estado da sessão
    df_conta = st.session_state.df_conta.copy()
    df_faturas = st.session_state.df_fatura.copy()
    df_clientes = st.session_state.df_clientes.copy()

    # Converter datas para formato datetime
    df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')
    df_conta['datapagamento'] = pd.to_datetime(df_conta['datapagamento'], errors='coerce')

    hoje = pd.Timestamp.now()

    # Merge com faturas para obter o codcliente
    df_conta_faturas = pd.merge(
        df_conta, df_faturas, left_on='codfatura', right_on='codfatura', how='left'
    )

    # Merge com clientes para obter os nomes
    df_conta_clientes = pd.merge(
        df_conta_faturas, df_clientes, left_on='codcliente', right_on='codcliente', how='left'
    )

    # Filtrar pelos clientes selecionados
    if clientes_selecionados_codigos:
        df_conta_clientes = df_conta_clientes[
            df_conta_clientes['codcliente'].isin(clientes_selecionados_codigos)
        ]

    # Faturas Pagas
    df_pagas = df_conta_clientes[
        df_conta_clientes['valorpagamento'] >= df_conta_clientes['valorvencimento']
    ]
    total_pagas = df_pagas['valorvencimento'].sum()
    quantidade_pagas = df_pagas.shape[0]

    # Faturas em Aberto
    df_aberto = df_conta_clientes[
        (df_conta_clientes['valorpagamento'] < df_conta_clientes['valorvencimento']) &
        (df_conta_clientes['datavencimento'] >= hoje)
    ]
    total_aberto = df_aberto['valorvencimento'].sum()
    quantidade_aberto = df_aberto.shape[0]

    # Faturas Vencidas
    df_vencidas = df_conta_clientes[
        (df_conta_clientes['datavencimento'] < hoje) &
        (
            (df_conta_clientes['valorpagamento'].isna()) |
            (df_conta_clientes['valorpagamento'] < df_conta_clientes['valorvencimento'])
        )
    ]
    total_vencidas = df_vencidas['valorvencimento'].sum()
    quantidade_vencidas = df_vencidas.shape[0]

    # Adiantamentos
    df_adiantamento = df_conta_clientes[
        (df_conta_clientes['valorpagamento'] > 0) &
        (df_conta_clientes['valorpagamento'] < df_conta_clientes['valorvencimento'])
    ]
    total_adiantamento = df_adiantamento['valorvencimento'].sum()
    quantidade_adiantamento = df_adiantamento.shape[0]

    # Média de Atraso
    df_vencidas['dias_atraso'] = (hoje - df_vencidas['datavencimento']).dt.days
    media_atraso = df_vencidas['dias_atraso'].mean() if not df_vencidas.empty else 0

    # Retornar os resultados
    return {
        "pagas": (quantidade_pagas, total_pagas),
        "aberto": (quantidade_aberto, total_aberto),
        "vencidas": (quantidade_vencidas, total_vencidas),
        "adiantamento": (quantidade_adiantamento, total_adiantamento),
        "media_atraso": media_atraso
    }
def calcular_vencimentos_por_cliente(clientes_selecionados_codigos):
    """
    Calcula os vencimentos por cliente, incluindo vencidas e a vencer.
    """
    # Obter os DataFrames do estado da sessão
    df_duplicatas = st.session_state.df_conta.copy()
    df_faturas = st.session_state.df_fatura.copy()
    df_clientes = st.session_state.df_clientes.copy()

    # Converter datas para formato datetime
    df_duplicatas['datavencimento'] = pd.to_datetime(df_duplicatas['datavencimento'], errors='coerce')
    df_duplicatas['datapagamento'] = pd.to_datetime(df_duplicatas['datapagamento'], errors='coerce')

    hoje = pd.Timestamp.now()

    # Filtrar duplicatas vencidas e não pagas
    df_vencidos = df_duplicatas[
        (df_duplicatas['datavencimento'] < hoje) &
        (
            (df_duplicatas['valorpagamento'].isna()) |
            (df_duplicatas['valorpagamento'] < df_duplicatas['valorvencimento'])
        )
    ]

    # Filtrar duplicatas a vencer
    df_a_vencer = df_duplicatas[
        (df_duplicatas['datavencimento'] >= hoje) &
        (
            (df_duplicatas['valorpagamento'].isna()) |
            (df_duplicatas['valorpagamento'] < df_duplicatas['valorvencimento'])
        )
    ]

    # Fazer merge com faturas para obter `codcliente`
    df_vencidos_faturas = pd.merge(
        df_vencidos, df_faturas, left_on='codfatura', right_on='codfatura', how='left'
    )
    df_a_vencer_faturas = pd.merge(
        df_a_vencer, df_faturas, left_on='codfatura', right_on='codfatura', how='left'
    )

    # Fazer merge com clientes para obter os nomes
    df_vencidos_clientes = pd.merge(
        df_vencidos_faturas, df_clientes, left_on='codcliente', right_on='codcliente', how='left'
    )
    df_a_vencer_clientes = pd.merge(
        df_a_vencer_faturas, df_clientes, left_on='codcliente', right_on='codcliente', how='left'
    )

    # Filtrar pelos clientes selecionados, se fornecidos
    if clientes_selecionados_codigos:
        df_vencidos_clientes = df_vencidos_clientes[
            df_vencidos_clientes['codcliente'].isin(clientes_selecionados_codigos)
        ]
        df_a_vencer_clientes = df_a_vencer_clientes[
            df_a_vencer_clientes['codcliente'].isin(clientes_selecionados_codigos)
        ]

    # Agrupar vencidos por cliente
    df_vencidos_resultado = df_vencidos_clientes.groupby('nome', as_index=False).agg({
        'valorvencimento': 'sum',
        'codfatura': 'count'
    }).rename(columns={
        'nome': 'Cliente',
        'valorvencimento': 'Total Vencido',
        'codfatura': 'Quantidade Vencida'
    })

    # Agrupar a vencer por cliente
    df_a_vencer_resultado = df_a_vencer_clientes.groupby('nome', as_index=False).agg({
        'valorvencimento': 'sum',
        'codfatura': 'count'
    }).rename(columns={
        'nome': 'Cliente',
        'valorvencimento': 'Total A Vencer',
        'codfatura': 'Quantidade A Vencer'
    })

    # Obter totais gerais
    total_vencido = df_vencidos_resultado['Total Vencido'].sum()
    quantidade_vencida = df_vencidos_resultado['Quantidade Vencida'].sum()

    total_a_vencer = df_a_vencer_resultado['Total A Vencer'].sum()
    quantidade_a_vencer = df_a_vencer_resultado['Quantidade A Vencer'].sum()

    # Exibir os KPIs
    col1, col2 = st.columns(2)

    with col1:
        bloco_kpi_estilizado_personalizado(
            titulo="Faturas Vencidas",
            qtd=quantidade_vencida,
            valor=f"R${trocadot(total_vencido)}",
            cabeca1="Qtd",
            cabeca2="Valor"
        )

    with col2:
        bloco_kpi_estilizado_personalizado(
            titulo="Faturas A Vencer",
            qtd=quantidade_a_vencer,
            valor=f"R${trocadot(total_a_vencer)}",
            cabeca1="Qtd",
            cabeca2="Valor"
        )

    # Retornar os DataFrames para exibição detalhada (opcional)
    # return df_vencidos_resultado, df_a_vencer_resultado




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

def exibir_metricas_caminhoes(total_caminhoes, peso_total, df):
    """Exibe as métricas dos caminhões usando colunas."""
    col1, col2 = st.columns(2)

    with col1:
        bloco_kpi_estilizado_personalizado(
            titulo="Caminhões",
            qtd=total_caminhoes,
            valor=f"{trocadot(peso_total)}t",
            cabeca1="Qtd",
            cabeca2="Peso Carregado"

        )
    with col2:

        # df = st.session_state.df_conhecimento_filtrado

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


def custo_operacional(df):
    """
    Exibe a análise de custos operacionais, incluindo freteMotorista e pedágio,
    agora no formato KPI estilizado.
    """
    # df = st.session_state.df_conhecimento_filtrado

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
        qtd=f"R${trocadot(custo_frete_motorista)}",
        valor=f"R${trocadot(custo_pedagio)}",
        valor1=f"R${trocadot(custo_total)}",
        cabeca1="Motorista",
        cabeca2="Pedagio",
        cabeca3="Total"
    )



def main():
    st.set_page_config(layout="wide")

    # Se não estiver logado, exibir tela de login
    if not st.session_state.get("logged_in", False):
        entrar()
        return  # Impede execução do restante do código se não logado

    with st.spinner("Carregando dados..."):
        load_data()  # Função que carrega df_conhecimento, df_conta, df_cliente, etc.


    # Aba principal
    tab1, tab2 = st.tabs(["Resumo Geral", "Detalhes por Cliente"])
    
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

        df_conhecimento = st.session_state.df_conhecimento.copy()

        # Converter a coluna 'data' para datetime
        df_conhecimento['data'] = pd.to_datetime(df_conhecimento['data'], errors='coerce')
        df_conhecimento = df_conhecimento.dropna(subset=['data'])

        df_filtrado = df_conhecimento[
            (df_conhecimento['data'] >= data_inicio) & (df_conhecimento['data'] <= data_fim)
        ]

        # Filtro por codunidadeembarque
        with col2:
            lista_filiais = sorted(df_filtrado['codunidadeembarque'].dropna().unique())
            lista_opcoes = ["Todos"] + list(lista_filiais)

            unidades_selecionadas = st.multiselect(
                "Selecione a(s) unidade(s) de embarque:",
                options=lista_opcoes,
                default=["Todos"]
            )

            if "Todos" in unidades_selecionadas:
                unidades_filtradas = lista_filiais
            else:
                unidades_filtradas = unidades_selecionadas

        # Aplicar filtro por unidade
        df_filtrado = df_filtrado[df_filtrado['codunidadeembarque'].isin(unidades_filtradas)]

        # KPIs (Emissões)
        if not df_filtrado.empty:
            calcular_kpis(df_filtrado)
        else:
            st.warning("Nenhum registro de fatura encontrado para os filtros selecionados.")

        # Calcular e exibir parcelas em aberto
        df_conta = st.session_state.df_conta.copy()
        df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')

        df_filtrado_conta = df_conta[
            (df_conta['datavencimento'] >= data_inicio) &
            (df_conta['datavencimento'] <= data_fim)
        ]

       # Certifique-se de que 'df_filtrado_conta' contém os dados filtrados corretamente
        if df_filtrado_conta is not None and not df_filtrado_conta.empty:
            # Chamada da função de cálculo
            resultados = calcular_parcelas_em_aberto(df_filtrado_conta)

            # Desempacotando os resultados
            df_adiantamento, qtd_adiantamento, total_adiantamento, \
            df_saldo, qtd_saldo, total_saldo, \
            df_vencidos, qtd_vencidos, total_vencidos = resultados

            # Verifica se há parcelas para exibir
            if qtd_adiantamento > 0 or qtd_saldo > 0 or qtd_vencidos > 0:
                exibir_parcelas_em_aberto(
                    df_adiantamento, qtd_adiantamento, total_adiantamento,
                    df_saldo, qtd_saldo, total_saldo,
                    df_vencidos, qtd_vencidos, total_vencidos
                )
            else:
                st.info("Nenhuma parcela em aberto ou vencida encontrada nesse intervalo.")
        else:
            st.warning("Nenhum dado disponível para o intervalo selecionado. Verifique os filtros.")

        # Métricas de caminhões
        if not df_filtrado.empty:
            total_caminhoes, peso_total = calcular_metricas_caminhoes(df_filtrado)
            exibir_metricas_caminhoes(total_caminhoes, peso_total, df_filtrado)

    with tab2:
        # Clientes
        df_clientes = st.session_state.df_clientes.copy()

        # Pode ser que df_filtrado esteja vazio se não houve filtros válidos
        if df_filtrado.empty:
            st.warning("Não há dados para mostrar detalhes por cliente.")
            return

        # Encontrar o pedido mais recente
        df_filtrado['data'] = pd.to_datetime(df_filtrado['data'])
        pedido_mais_recente = df_filtrado.loc[df_filtrado['data'].idxmax()]
        codcliente_mais_recente = pedido_mais_recente['codcliente']

        # Descobrir nome do cliente
        try:
            cliente_mais_recente = df_clientes[df_clientes['codcliente'] == codcliente_mais_recente]['nome'].values[0]
        except IndexError:
            cliente_mais_recente = "Todos"

        # Criar mapeamento nome->código
        df_merged = pd.merge(df_clientes, df_filtrado, on='codcliente', how='right')
        map_nome_codigo = dict(zip(df_merged['nome'], df_merged['codcliente']))

        lista_opcoes = ["Todos"] + list(map_nome_codigo.keys())

        clientes_selecionados = st.multiselect(
            "Selecione os clientes:",
            options=lista_opcoes,
            default=[cliente_mais_recente]  # Seleciona automaticamente o cliente mais recente
        )

        # Obter códigos dos clientes selecionados
        clientes_selecionados_codigos = [
            map_nome_codigo[nome]
            for nome in clientes_selecionados
            if nome != "Todos"
        ]

        if "Todos" in clientes_selecionados:
            df_filtrado_cliente = df_filtrado
        else:
            df_filtrado_cliente = df_filtrado[df_filtrado['codcliente'].isin(clientes_selecionados_codigos)]

        if not df_filtrado_cliente.empty:
            calcular_kpis(df_filtrado_cliente)
            custo_operacional(df_filtrado_cliente)

            mostrar_detalhes_pedidos_cliente(df_filtrado_cliente, clientes_selecionados_codigos)

            # Exibir métricas de caminhões
            total_caminhoes, peso_total = calcular_metricas_caminhoes(df_filtrado_cliente)
            exibir_metricas_caminhoes(total_caminhoes, peso_total, df_filtrado_cliente)
        else:
            st.warning("Nenhum registro de fatura encontrado para os clientes selecionados.")


        # Carregar DataFrames da sessão
        df_duplicatas = st.session_state.df_conta.copy()
        df_faturas = st.session_state.df_fatura.copy()  # Ou carregue o DataFrame de faturas
        df_clientes = st.session_state.df_clientes.copy()

        # Verificar se os DataFrames não estão vazios
        if df_duplicatas.empty or df_faturas.empty or df_clientes.empty:
            st.warning("Não há dados disponíveis para calcular vencimentos por cliente.")
        else:
            # Calcular vencimentos por cliente
            calcular_vencimentos_por_cliente(clientes_selecionados_codigos)
            


    # tab3 poderia estar aqui caso precise exibir algo adicional


if __name__ == "__main__":
    main()
