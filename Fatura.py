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
from streamlit_cookies_manager import EncryptedCookieManager



# Configuração da página - primeira chamada do Streamlit


st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Configure o gerenciador de cookies
cookies = EncryptedCookieManager(
    prefix="my_app_",  # Prefixo para diferenciar os cookies desta aplicação
    password="123adminnimda321"  # Substitua por uma senha forte
)

# Necessário para inicializar os cookies no Streamlit
if not cookies.ready():
    st.stop()

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

import json

def salvar_usuario_em_cookie(usuario, role):
    """
    Salva as informações do usuário no cookie com validade de 30 dias.
    """
    # Definir a data de expiração para 30 dias a partir de agora
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    # Serializar os valores como strings
    cookies["usuario"] = json.dumps({"value": usuario, "expires_at": expires_at})
    cookies["role"] = json.dumps({"value": role, "expires_at": expires_at})
    cookies["login_time"] = json.dumps({"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "expires_at": expires_at})
    
    # Salvar as mudanças nos cookies
    cookies.save()



def entrar():
    st.title("Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        autenticado, role_encontrada = verificar_usuario_senha(usuario, senha)

        if autenticado:
            st.session_state["logged_in"] = True
            st.session_state["username"] = usuario
            st.session_state["role"] = role_encontrada

            # Salvar usuário nos cookies
            salvar_usuario_em_cookie(usuario, role_encontrada)

            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def verificar_usuario_pelo_cookie():
    """
    Verifica se o usuário está logado pelos cookies.
    """
    try:
        usuario = json.loads(cookies.get("usuario"))
        role = json.loads(cookies.get("role"))
        login_time = json.loads(cookies.get("login_time"))

        if usuario and role:
            st.session_state["logged_in"] = True
            st.session_state["username"] = usuario["value"]
            st.session_state["role"] = role["value"]
            return True
    except (TypeError, json.JSONDecodeError):
        pass

    return False




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
        <div style="background-color: #11804B; color: #FEFEFE; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #324F9E; color: #FEFEFE; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FEFEFE;">Qtd</th>
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


def calcular_kpis(df_filtrado, df_fatura_filtrados):
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
        
        exibir_grafico_metodos(df_fatura_filtrados)
    # with col3:
    #     bloco_kpi_estilizado(
    #         titulo="CANCELADAS",
    #         qtd=taxa_cancelamento,
    #         valor=valor_canceladas_str
    #     )


def calcular_kpis_cliente(df_filtrado):
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


import matplotlib.pyplot as plt

def exibir_grafico_metodos(df_fatura):

    print(type(df_fatura['codcondicao']))


    # Confirmação de colunas
    if 'codcondicao' not in df_fatura.columns or 'valor' not in df_fatura.columns:
        raise KeyError("As colunas 'codcondicao' e/ou 'valor' estão ausentes no DataFrame.")

    # Converte a coluna 'codcondicao' para tipo numérico
    # Se houver valores não convertíveis, serão transformados em NaN
    df_fatura['codcondicao'] = pd.to_numeric(df_fatura['codcondicao'], errors='coerce')
    
    # Mapeamento de métodos
    mapping = {
    1: {"Método": "Digital SCD", "Parcelas": 1},
    3: {"Método": "Digital SCD", "Parcelas": 2},
    4: {"Método": "Rede Credenciada", "Parcelas": 3},
    5: {"Método": "Rede Credenciada", "Parcelas": 4},
    6: {"Método": "Rede Credenciada", "Parcelas": 5},
    7: {"Método": "Rede Credenciada", "Parcelas": 6},
    8: {"Método": "Rede Credenciada", "Parcelas": 7},
    9: {"Método": "Rede Credenciada", "Parcelas": 8},
    12: {"Método": "Digital SCD", "Parcelas": 1},
    14: {"Método": "Digital SCD", "Parcelas": 1},
    13: {"Método": "Rede Credenciada", "Parcelas": 10},
    15: {"Método": "Rede Credenciada", "Parcelas": 9},
    19: {"Método": "Digital SCD", "Parcelas": 2},
    20: {"Método": "Digital SCD", "Parcelas": 1},
    21: {"Método": "Digital SCD", "Parcelas": 1},
    22: {"Método": "TRC", "Parcelas": 60},
    23: {"Método": "Digital SCD", "Parcelas": 1},
    24: {"Método": "Digital SCD", "Parcelas": 1},
    25: {"Método": "Digital SCD", "Parcelas": 1},
    26: {"Método": "Digital SCD", "Parcelas": 1},
    17: {"Método": "Digital SCD", "Parcelas": 1},
    27: {"Método": "Digital SCD", "Parcelas": 1},
    2: {"Método": "Digital SCD", "Parcelas": 1},
    28: {"Método": "Rede Credenciada", "Parcelas": 1},
    29: {"Método": "TRC", "Parcelas": 48},
    30: {"Método": "Digital SCD", "Parcelas": 1},
    31: {"Método": "Digital SCD", "Parcelas": 1},
    32: {"Método": "Digital SCD", "Parcelas": 1},
    33: {"Método": "Digital SCD", "Parcelas": 1},
    34: {"Método": "Digital SCD", "Parcelas": 1},
    35: {"Método": "Digital SCD", "Parcelas": 1},
    18: {"Método": "Digital SCD", "Parcelas": 2},
    11: {"Método": "TRC", "Parcelas": 12},
    16: {"Método": "TRC", "Parcelas": 12},
    36: {"Método": "TRC", "Parcelas": 11},
    37: {"Método": "TRC", "Parcelas": 26},
}


    # Adicionar colunas 'Método' e 'Parcelas' no DataFrame
    df_fatura['Método'] = df_fatura['codcondicao'].map(lambda x: mapping.get(x, {}).get("Método", "Outros"))
    df_fatura['Parcelas'] = df_fatura['codcondicao'].map(lambda x: mapping.get(x, {}).get("Parcelas", 0))

    # Agrupando os dados por Método e somando os valores
    grafico_data = df_fatura.groupby('Método', as_index=False)['valor'].sum()

    fig = plt.figure(figsize=(3, 1.3))
    plt.pie(
        grafico_data['valor'],
        labels=grafico_data['Método'],
        autopct='%1.1f%%',
        startangle=40
    )
    plt.title('Soma de Valor (%) por Método')

    st.pyplot(fig)


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

def calcular_parcelas_por_dia(df_conta):
    """Filtra as parcelas a receber nos próximos 5 dias e agrupa por dia."""
    df_conta['datavencimento'] = pd.to_datetime(df_conta['datavencimento'], errors='coerce')
    df_conta['datapagamento'] = pd.to_datetime(df_conta['datapagamento'], errors='coerce')

    hoje = pd.Timestamp.now()
    cinco_dias = hoje + pd.Timedelta(days=5)

    # Filtrar parcelas nos próximos 5 dias
    df_proximos = df_conta[
        (df_conta['datavencimento'] >= hoje) &
        (df_conta['datavencimento'] <= cinco_dias) &
        (
            (df_conta['valorpagamento'].isna()) |
            (df_conta['valorpagamento'] < df_conta['valorvencimento'])
        )
    ]

    # Agrupar por dia
    agrupado_por_dia = df_proximos.groupby(df_proximos['datavencimento'].dt.date).agg({
        'valorvencimento': 'sum',
        'codfatura': 'count'  # Opcional: calcular o número de faturas por dia
    }).rename(columns={
        'valorvencimento': 'Total a Receber',
        'codfatura': 'Quantidade'
    }).reset_index().rename(columns={'datavencimento': 'Dia'})

    return agrupado_por_dia

def exibir_parcelas_por_dia(df_por_dia):
    """Exibe os valores a receber organizados por dia."""
    st.markdown("### Valores a Receber por Dia")

    if df_por_dia.empty:
        st.info("Nenhuma parcela a receber nos próximos 5 dias.")
        return

    for _, row in df_por_dia.iterrows():
        dia = row['Dia']
        total = row['Total a Receber']
        quantidade = row['Quantidade']

        bloco_kpi_estilizado(
            titulo=f"{dia.strftime('%d/%m/%Y')}",
            qtd=quantidade,
            valor=f"R${trocadot(total)}"
        )

def calcular_metricas_caminhoes(df):
    """Calcula métricas relacionadas aos caminhões e fretes."""
    try:
        # Quantidade de Viagens
        total_viagens = len(df)

        # Cliente Principal (cliente com maior valor de frete)
        cliente_principal = (
            df.groupby('codcliente')['freteempresa']
            .sum()
            .idxmax() if 'codcliente' in df.columns and not df.empty else None
        )

        # Valor associado ao Cliente Principal
        valor_cliente_principal = (
            df.groupby('codcliente')['freteempresa']
            .sum()
            .get(cliente_principal, 0.0) if cliente_principal else 0.0
        )

        # Valor Frete Empresa Total Embarcado
        valor_total_embarcado = df['freteempresa'].sum() if 'freteempresa' in df.columns else 0.0

        # Peso (em toneladas)
        peso_em_toneladas = (
            df['pesosaida'].sum() / 1000 if 'pesosaida' in df.columns else 0.0
        )

        # Total Embarcadas
        total_embarcadas = df['codveiculo'].nunique() if 'codveiculo' in df.columns else 0

        return total_viagens, cliente_principal, valor_cliente_principal, valor_total_embarcado, peso_em_toneladas, total_embarcadas

    except Exception as e:
        print(f"Erro ao calcular métricas: {str(e)}")
        return 0, None, 0.0, 0.0, 0.0, 0



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
        <div style="background-color: #11804B; color: #FEFEFE; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #324F9E; color: #FEFEFE; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FEFEFE;">{cabeca1}</th>
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

def exibir_metricas_gerais(total_viagens, cliente_principal, valor_cliente_principal, valor_total_embarcado, peso_em_toneladas, total_embarcadas):
    """Exibe as métricas gerais no dashboard."""
    st.markdown("### Métricas Gerais")

    col1, col2, col3 = st.columns(3)

    with col1:
        bloco_kpi_estilizado_personalizado(
            titulo="Entregas",
            qtd=total_viagens,
            valor=f"{trocadot(peso_em_toneladas)}t",
            cabeca1="Qtd",
            cabeca2="Peso Carregado"
        )

    with col2:
        bloco_kpi_estilizado(
            titulo="Cliente Principal",
            qtd=cliente_principal if cliente_principal else "N/A",
            valor=f"R${trocadot(valor_cliente_principal)}"
        )

    with col3:
        bloco_kpi_estilizado(
            titulo="Embarcados",
            qtd=total_embarcadas,
            valor=f"R${trocadot(valor_total_embarcado)}"
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
        <div style="background-color: #11804B; color: #FEFEFE; text-align: center; padding: 8px; font-weight: bold;">
            {titulo}
        </div>
        <table style="width: 100%; border-collapse: collapse;">
            <!-- Cabeçalho: fundo dourado -->
            <thead>
                <tr style="background-color: #324F9E; color: #FEFEFE; text-align: center;">
                    <th style="padding: 5px; border-right: 1px solid #FEFEFE;">{cabeca1}</th>
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
    Exibe a análise de custos operacionais, incluindo freteMotorista, pedágio, margem bruta e margem %.
    """
    # Gasto total com Frete Motorista
    custo_frete_motorista = (
        df['fretemotorista'].sum() if 'fretemotorista' in df.columns else 0
    )

    # Gasto total com Pedágio
    custo_pedagio = (
        df['valorpedagio'].sum() if 'valorpedagio' in df.columns else 0
    )

    # Receita total
    receita_total = (
        df['freteempresa'].sum() if 'freteempresa' in df.columns else 0
    )
    
    # Custo total
    custo_total = custo_frete_motorista + custo_pedagio

    # Margem Bruta
    margem_bruta = receita_total - custo_total

    # Margem %
    margem_percentual = (margem_bruta / receita_total * 100) if receita_total > 0 else 0
    col1, col2, col3 = st.columns(3)
    with col1:
        # Exibição dos KPIs
        bloco_kpi_estilizado_personalizado_tres(
            titulo="Custos Operacionais",
            qtd=f"R${trocadot(custo_frete_motorista)}",
            valor=f"R${trocadot(custo_pedagio)}",
            valor1=f"R${trocadot(custo_total)}",
            cabeca1="Motorista",
            cabeca2="Pedágio",
            cabeca3="Total"
        )
    with col2:
        bloco_kpi_estilizado_personalizado_tres(
            titulo="Margem",
            qtd=f"R${trocadot(margem_bruta)}",
            valor=f"{margem_percentual:.2f}%",
            valor1=f"R${trocadot(receita_total)}",
            cabeca1="Bruta",
            cabeca2="%",
            cabeca3="Receita Total"
        )


# Função para formatar o CNPJ
def formatar_cnpj(cnpj):
    if cnpj and len(cnpj) == 14:  # Verifica se o CNPJ tem 14 dígitos
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj  # Retorna como está caso não tenha 14 dígitos

def main():
    # Configuração da página - esta deve ser a primeira chamada ao Streamlit

    # Verificar login pelos cookies
    if not verificar_usuario_pelo_cookie() and not st.session_state.get("logged_in", False):
        entrar()
        return  # Impede execução do restante do código se não logado

    with st.spinner("Carregando dados..."):
        load_data()  # Função que carrega df_conhecimento, df_conta, df_cliente, etc.

    # Aba principal
    tab1, tab2 = st.tabs(["Resumo Geral", "Detalhes por Cliente"])
    
    with tab1:
        st.header("Filtros")
        col1, col2, col3 = st.columns(3)

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
            lista_uniembarque = sorted(df_filtrado['codunidadeembarque'].dropna().unique())
            lista_opcoes = ["Todos"] + list(lista_uniembarque)

            unidades_selecionadas = st.multiselect(
                "Selecione a(s) unidade(s) de embarque:",
                options=lista_opcoes,
                default=["Todos"]
            )

            if "Todos" in unidades_selecionadas:
                unidades_filtradas = lista_uniembarque
            else:
                unidades_filtradas = unidades_selecionadas

        with col3:
            # Formata os CNPJs antes de criar a lista
            df_filtrado['emit_CNPJ_formatado'] = df_filtrado['emit_CNPJ'].dropna().apply(formatar_cnpj)

            # Mapeia os CNPJs formatados de volta para o original
            cnpj_map = dict(zip(df_filtrado['emit_CNPJ_formatado'], df_filtrado['emit_CNPJ']))

            # Lista de filiais com CNPJs formatados
            lista_filiais = sorted(df_filtrado['emit_CNPJ_formatado'].dropna().unique())
            lista_opcoes = ["Todos"] + list(lista_filiais)

            # Multiselect para selecionar as filiais
            unidades_selecionadas = st.multiselect(
                "Selecione a(s) filial:",
                options=lista_opcoes,
                default=["Todos"]
            )

            # Converte os CNPJs formatados selecionados de volta ao original
            if "Todos" in unidades_selecionadas:
                unidades_filtradasFil = df_filtrado['emit_CNPJ'].dropna().unique()
            else:
                unidades_filtradasFil = [cnpj_map[cnpj] for cnpj in unidades_selecionadas if cnpj in cnpj_map]

        # Aplicar filtro por unidade
        df_filtrado = df_filtrado[df_filtrado['codunidadeembarque'].isin(unidades_filtradas)]
        df_filtrado = df_filtrado[df_filtrado['emit_CNPJ'].isin(unidades_filtradasFil)]

        df_fatura = st.session_state.df_fatura.copy()  # Ou carregue o DataFrame de faturas
         
        df_filtrado_fatura = df_fatura[
            (df_fatura['data'] >= data_inicio) &
            (df_fatura['data'] <= data_fim)
        ]



        # KPIs (Emissões)
        if not df_filtrado.empty:
            calcular_kpis(df_filtrado, df_filtrado_fatura)
            
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

            # Calcular valores por dia
            # df_por_dia = calcular_parcelas_por_dia(df_filtrado_conta)

            # Exibir valores por dia
            # exibir_parcelas_por_dia(df_por_dia)

        else:
            st.warning("Nenhum dado disponível para o intervalo selecionado. Verifique os filtros.")

        custo_operacional(df_filtrado)

        # Métricas de caminhões
        if not df_filtrado.empty:
            # Calcular métricas gerais
            total_viagens, cliente_principal,valor_cliente, valor_total_embarcado, peso_em_toneladas, total_embarcadas = calcular_metricas_caminhoes(df_filtrado)

            # Exibir métricas gerais
            exibir_metricas_gerais(total_viagens, cliente_principal,valor_cliente, valor_total_embarcado, peso_em_toneladas, total_embarcadas)
        else:
            st.warning("Nenhum dado disponível para calcular métricas gerais.")



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
            calcular_kpis_cliente(df_filtrado_cliente)
            custo_operacional(df_filtrado_cliente)

            mostrar_detalhes_pedidos_cliente(df_filtrado_cliente, clientes_selecionados_codigos)

            # Exibir métricas de caminhões
            # Ajuste a chamada para capturar todos os retornos da função
            total_viagens, cliente_principal,valor_cliente, valor_total_embarcado, peso_em_toneladas, total_embarcadas = calcular_metricas_caminhoes(df_filtrado_cliente)

            # Exiba as métricas gerais
            exibir_metricas_gerais(total_viagens, cliente_principal,valor_cliente, valor_total_embarcado, peso_em_toneladas, total_embarcadas)

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
