import pymongo
from pymongo.errors import PyMongoError
import streamlit as st

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
    if 'autenticador_status' not in st.session_state:
        st.session_state['autenticador_status'] = None
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
            st.session_state['autenticador_status'] = True
            st.session_state['username'] = usuario
            st.session_state['role'] = role_encontrada
            st.success("Login realizado com sucesso!")
        else:
            st.session_state['autenticador_status'] = False
            st.error("Usuário ou senha inválidos.")

    return st.session_state['autenticador_status'], st.session_state['username'], st.session_state['role']
    # return usuario, senha, role_encontrada


