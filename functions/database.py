import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine, text

# CONECTION
@st.cache_resource
def obtener_engine():
    try:
        return create_engine(
            f"mysql+pymysql://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}"
            f"@{st.secrets['DB_SERVER']}:3306"
            f"/{st.secrets['DB_NAME']}?charset=utf8mb4"
        )
    except Exception as e:
        st.error(f"Error al construir la conexión: {e}")
        return None

# DATOS CRUD
@st.cache_data(ttl=60)
def cargar_datos(_engine):
    with _engine.connect() as conexion:
        df = pd.read_sql("SELECT * FROM edunied_actividades ORDER BY fecha DESC, id DESC", conexion)
    return df

CAMPOS_TABLA = [
    "tipo", "fecha", "dia_semana", "capacitador", "auxiliar", "tipo_auxilio",
    "modalidad", "inicio", "fin", "lugar", "es_comunidad", "asistentes",
]
def insertar_registro(engine, datos: dict):
    columnas = ", ".join(CAMPOS_TABLA)
    placeholders = ", ".join([f":{c}" for c in CAMPOS_TABLA])
    sql = text(f"INSERT INTO edunied_actividades ({columnas}) VALUES ({placeholders})")
    with engine.begin() as conexion:
        conexion.execute(sql, datos)


def actualizar_registro(engine, id_registro: int, datos: dict):
    set_clause = ", ".join([f"{c} = :{c}" for c in CAMPOS_TABLA])
    sql = text(f"UPDATE edunied_actividades SET {set_clause} WHERE id = :id_registro")
    datos_con_id = {**datos, "id_registro": id_registro}
    with engine.begin() as conexion:
        conexion.execute(sql, datos_con_id)


def eliminar_registro(engine, id_registro: int):
    sql = text(f"DELETE FROM edunied_actividades WHERE id = :id_registro")
    with engine.begin() as conexion:
        conexion.execute(sql, {"id_registro": id_registro})

def log_event(conn, session_id, ip, session_state, evento, pagina=None):
    try:
        state_dict = dict(session_state)
        state_str  = json.dumps(state_dict, ensure_ascii=False, default=str)
        with conn.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO acceso_logs (session_id, ip, session_state, evento, pagina)
                    VALUES (:session_id, :ip, :session_state, :evento, :pagina)
                """),
                {
                    "session_id": session_id,
                    "ip": ip,
                    "session_state": state_str[:65535],
                    "evento": evento,
                    "pagina": pagina
                }
            )
    except Exception as e:
        print(f"Error guardando log: {e}")