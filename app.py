import uuid
import streamlit as st
from functions.database import obtener_engine, cargar_datos, log_event
from views import home, capturar, buscar, stats, login

st.set_page_config(
    page_title="EDUNIED",
    page_icon="assets/icon_sectech.png",
    menu_items={
        'Report a bug': 'https://sectechnologies.vercel.app/',
        'About': "# EDUNIED\nUnidad de Estadística | Educación."
    },
    layout='wide'
)

def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer-badge-wrap">
        <div class="footer-badge">
            <span class="copy">© 2026</span>
            <span class="brand">EDUNIED</span>
            <span class="sep">|</span>
            <span class="copy">Desarrollado por</span>
            <a href="https://taquitoo3000.github.io/isael/">SECtech</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

load_css()
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
if not st.session_state.autenticado:
    login.render()
engine = obtener_engine()
try:
    df = cargar_datos(engine)
except Exception as e:
    st.error(f"Error al leer datos de la base de datos: {e}")
    st.stop()
if "logged" not in st.session_state:
    log_event(
        engine,
        st.session_state.session_id,
        st.session_state.usuario,
        {"":""},
        "NEW_SESSION",
        None
    )
    st.session_state.logged = True

with st.sidebar:
    st.badge(f"Usuario: **{st.session_state.get("usuario")}**",
                     color='violet')
    if st.sidebar.button("Cerrar sesión", icon=":material/close:"):
        st.session_state.autenticado = False
        st.rerun()
    if st.button("Refrescar datos",icon=":material/refresh:"):
        st.cache_data.clear()
        st.rerun()

pagina_home = st.Page(
    lambda: home.render(df),
    title="Inicio", icon=":material/home:", url_path="inicio", default=True,
)
pagina_capturar = st.Page(
    lambda: capturar.render(df, engine),
    title="Capturar", icon=":material/add_circle:", url_path="capturar",
)
pagina_buscar = st.Page(
    lambda: buscar.render(df, engine),
    title="Buscar", icon=":material/search:", url_path="buscar",
)
pagina_stats = st.Page(
    lambda: stats.render(df),
    title="Estadísticas", icon=":material/bar_chart:", url_path="estadisticas",
)

pagina_seleccionada = st.navigation(
    [pagina_home, pagina_capturar, pagina_buscar, pagina_stats]
)
pagina_seleccionada.run()

render_footer()