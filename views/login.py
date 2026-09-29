import streamlit as st
import hashlib

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def render():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
                <div style="
                    background: #5c2d82;
                    padding: 2px 2px;
                    border-radius: 16px;
                    margin-bottom: 28px;
                    text-align: center;
                    box-shadow: 0 8px 24px rgba(128,85,171,0.25);
                ">
                    <h1 style="color: white; margin: 0; font-size: 2.2rem;">
                        EDUNIED
                    </h1>
                    <p style="color: white; font-size: 1.05rem;">
                        Coordinación de Educación | Software de la Unidad de Información Estadística y Documental
                    </p>
                    <span style="
                        display: inline-block;
                        background: rgba(255,255,255,0.18);
                        color: white;
                        padding: 4px 14px;
                        border-radius: 20px;
                        font-size: 0.78rem;
                        font-weight: 600;
                        letter-spacing: 0.5px;
                    ">
                        v1.0
                    </span>
                </div>
            """, unsafe_allow_html=True)
        with st.form("form_login"):
            usuario = st.selectbox(
                "**Usuario:**",
                options= [
                    'UNIED',
                    'Dirección'
                ],
                index=None,
                key='sel_miembro'
            )
            password = st.text_input("Contraseña", type="password")
            enviar = st.form_submit_button("Entrar")
        if enviar:
            usuarios_validos = st.secrets["usuarios"]
            h_password=hash_password(password)
            if usuario in usuarios_validos and h_password == usuarios_validos[usuario]:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()