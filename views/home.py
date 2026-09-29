import streamlit as st
import pandas as pd

def _icono_material(nombre, tamano="1.8rem", color="inherit"):
    return f'<span class="material-symbols-rounded" style="font-size:{tamano}; color:{color}; vertical-align:middle;">{nombre}</span>'

def _tarjeta_metrica(valor, etiqueta, icono):
    st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e9d9f7;
            border-radius: 14px;
            padding: 20px 16px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(128,85,171,0.10);
            height: 100%;
        ">
            <div style="margin-bottom: 4px; color: #8055AB;">{_icono_material(icono)}</div>
            <div style="font-size: 1.9rem; font-weight: 700; color: #7E00D4; line-height: 1.1;">
                {valor}
            </div>
            <div style="font-size: 0.85rem; color: #888; margin-top: 4px;">
                {etiqueta}
            </div>
        </div>
    """, unsafe_allow_html=True)


def _tarjeta_acceso(icono, titulo, descripcion, color="#8055AB"):
    st.markdown(f"""
        <div style="
            background: {color};
            border-radius: 14px;
            padding: 22px 20px;
            color: white;
            height: 100%;
            box-shadow: 0 6px 18px rgba(128,85,171,0.20);
        ">
            <div style="margin-bottom: 6px;">{_icono_material(icono, tamano="1.6rem", color="white")}</div>
            <div style="font-size: 1.05rem; font-weight: 700; margin-bottom: 4px;">
                {titulo}
            </div>
            <div style="font-size: 0.85rem; opacity: 0.9; line-height: 1.4;">
                {descripcion}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render(df):
    # ---------- HERO ----------
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

    # ---------- DESCRIPCIÓN INSTITUCIONAL ----------
    st.markdown("""
        <div style="
            background: #faf6fd;
            border-radius: 10px;
            padding: 20px 24px;
            margin-bottom: 32px;
        ">
            <p style="margin: 0; color: #4a4a4a; font-size: 0.98rem; line-height: 1.6;">
                <strong>EDUNIED</strong> centraliza el registro y seguimiento de las actividades
                de capacitación en derechos humanos que realiza la institución: cursos, talleres
                y asesorías impartidos en distintas modalidades y comunidades. Aquí puedes
                capturar nuevas sesiones, consultar y editar el historial, y revisar
                estadísticas de cobertura y carga de trabajo del equipo capacitador.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ---------- MÉTRICAS RÁPIDAS ----------
    st.markdown("#### Resumen general")
 
    if df is None or df.empty:
        st.info("Aún no hay actividades registradas. Comienza capturando una en el menú lateral.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            _tarjeta_metrica(len(df), "Sesiones registradas", "menu_book")
        with col2:
            _tarjeta_metrica(int(df["asistentes"].sum()), "Asistentes atendidos", "groups")
        with col3:
            _tarjeta_metrica(df["capacitador"].nunique(), "Capacitadores activos", "school")
        with col4:
            comunidades = (df["es_comunidad"].str.upper() == "SI").sum() if "es_comunidad" in df else 0
            _tarjeta_metrica(comunidades, "Sesiones en comunidad", "location_city")
 
    st.write("")
    st.markdown("#### Accesos rápidos")
 
    col1, col2, col3 = st.columns(3)
    with col1:
        _tarjeta_acceso("add_circle", "Capturar", "Registra una nueva sesión de capacitación.")
    with col2:
        _tarjeta_acceso("search", "Buscar / Editar", "Consulta, filtra y corrige registros existentes.")
    with col3:
        _tarjeta_acceso("bar_chart", "Estadísticas", "Cobertura, tendencias e índice de carga de trabajo.")
 
    st.caption("Usa el menú de la barra lateral para navegar entre secciones.")