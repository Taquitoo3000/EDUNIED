import streamlit as st
from datetime import date, time
from functions.calculos import campo_con_opciones, valores_existentes, calcular_dia_semana
from functions.database import insertar_registro

OPCIONES_MODALIDAD = ["PRESENCIAL", "VIRTUAL", "HÍBRIDO"]
OPCIONES_TIPO_AUXILIO = ["TOTAL", "PARCIAL", "NO APLICA"]
OPCIONES_SI_NO = ["SI", "NO"]

def render(df, engine):
    st.subheader("Registrar nueva capacitación")

    with st.form("form_captura", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            tipo = campo_con_opciones("Tipo", valores_existentes(df, "tipo"), "cap_tipo")
            fecha_val = st.date_input("Fecha", value=date.today(), key="cap_fecha")
            capacitador = campo_con_opciones("Capacitador", valores_existentes(df, "capacitador"), "cap_capacitador")

        with col2:
            auxiliar = campo_con_opciones("Auxiliar", valores_existentes(df, "auxiliar"), "cap_auxiliar")
            tipo_auxilio = campo_con_opciones("Tipo de auxilio", OPCIONES_TIPO_AUXILIO, "cap_tipo_auxilio")
            modalidad = campo_con_opciones("Modalidad", OPCIONES_MODALIDAD, "cap_modalidad")

        with col3:
            inicio_val = st.time_input("Hora de inicio", value=time(9, 0), key="cap_inicio")
            fin_val = st.time_input("Hora de fin", value=time(10, 0), key="cap_fin")
            lugar = campo_con_opciones("Lugar", valores_existentes(df, "lugar"), "cap_lugar")

        col4, col5 = st.columns(2)
        with col4:
            es_comunidad = st.radio("¿Es comunidad?", OPCIONES_SI_NO, horizontal=True, key="cap_comunidad")
        with col5:
            asistentes = st.number_input("Asistentes", min_value=0, step=1, key="cap_asistentes")

        guardar = st.form_submit_button("Guardar registro", type="primary")

    if guardar:
        if not tipo or not capacitador or not lugar:
            st.error("Tipo, capacitador y lugar son obligatorios.")
        else:
            datos = {
                "tipo": tipo,
                "fecha": fecha_val,
                "dia_semana": calcular_dia_semana(fecha_val),
                "capacitador": capacitador,
                "auxiliar": auxiliar,
                "tipo_auxilio": tipo_auxilio,
                "modalidad": modalidad,
                "inicio": inicio_val,
                "fin": fin_val,
                "lugar": lugar,
                "es_comunidad": es_comunidad,
                "asistentes": int(asistentes),
            }
            try:
                insertar_registro(engine, datos)
                st.cache_data.clear()
                st.success("Registro guardado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")