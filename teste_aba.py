import streamlit as st
import pandas as pd

# Simulando um DataFrame com os dados
data = {
    "cliente": ["Cliente A", "Cliente B", "Cliente C"],
    "total_toneladas": [50, 80, 30],
    "caminhoes": [
        [{"id": "Caminhão 1", "toneladas": 20}, {"id": "Caminhão 2", "toneladas": 30}],
        [{"id": "Caminhão 3", "toneladas": 50}, {"id": "Caminhão 4", "toneladas": 30}],
        [{"id": "Caminhão 5", "toneladas": 10}, {"id": "Caminhão 6", "toneladas": 20}],
    ],
}
df = pd.DataFrame(data)

# Abas principais
tab1, tab2, tab3 = st.tabs(["Resumo Geral", "Detalhes por Cliente", "Detalhes por Caminhão"])

# Aba 1: Resumo Geral
with tab1:
    st.header("Resumo Geral")
    st.write("Aqui está o total emitido e toneladas carregadas.")
    st.write(df[["cliente", "total_toneladas"]])

    # Selecionar cliente para ir à segunda aba
    cliente_selecionado = st.selectbox("Selecione um cliente para detalhes:", df["cliente"])

# Aba 2: Detalhes por Cliente
with tab2:
    st.header(f"Detalhes de {cliente_selecionado}")
    
    # Filtrar o DataFrame para o cliente selecionado
    detalhes_cliente = df[df["cliente"] == cliente_selecionado]
    st.write(detalhes_cliente[["cliente", "total_toneladas"]])

    # Exibir caminhões do cliente
    caminhões = detalhes_cliente["caminhoes"].iloc[0]
    st.write("Caminhões e Toneladas:")
    for caminhão in caminhões:
        st.write(f"- {caminhão['id']}: {caminhão['toneladas']} toneladas")

    # Selecionar caminhão para ir à terceira aba
    caminhão_selecionado = st.selectbox(
        "Selecione um caminhão para detalhes:",
        [c["id"] for c in caminhões],
    )

# Aba 3: Detalhes por Caminhão
with tab3:
    st.header(f"Detalhes do {caminhão_selecionado}")

    # Filtrar os detalhes do caminhão
    caminhão_detalhes = next(
        (c for c in caminhões if c["id"] == caminhão_selecionado), None
    )
    if caminhão_detalhes:
        st.write(f"O caminhão {caminhão_detalhes['id']} carregou {caminhão_detalhes['toneladas']} toneladas.")
