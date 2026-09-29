import streamlit as st
import pandas as pd
from datetime import time
from functions.calculos import valores_existentes, campo_con_opciones, calcular_dia_semana, convertir_a_time
from functions.database import actualizar_registro, eliminar_registro

OPCIONES_TIPO = ["CURSOS", "TALLER", "ASESORÍA", "OTRO"]
OPCIONES_MODALIDAD = ["PRESENCIAL", "VIRTUAL", "HÍBRIDO"]
OPCIONES_TIPO_AUXILIO = ["TOTAL", "PARCIAL", "NO APLICA"]
OPCIONES_SI_NO = ["SI", "NO"]

def render(df, engine):
    st.subheader("Buscar registros")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_capacitador = st.multiselect("Capacitador", valores_existentes(df, "capacitador"))
    with col2:
        f_tipo = st.multiselect("Tipo", valores_existentes(df, "tipo"))
    with col3:
        f_modalidad = st.multiselect("Modalidad", valores_existentes(df, "modalidad"))
    with col4:
        f_lugar = st.multiselect("Lugar", valores_existentes(df, "lugar"))

    col5, col6 = st.columns(2)
    with col5:
        rango_fechas = st.date_input(
            "Rango de fechas", value=(), key="f_rango_fechas"
        )
    with col6:
        texto_libre = st.text_input("Buscar texto libre (capacitador, auxiliar, lugar)")

    resultado = df.copy()
    if f_capacitador:
        resultado = resultado[resultado["capacitador"].isin(f_capacitador)]
    if f_tipo:
        resultado = resultado[resultado["tipo"].isin(f_tipo)]
    if f_modalidad:
        resultado = resultado[resultado["modalidad"].isin(f_modalidad)]
    if f_lugar:
        resultado = resultado[resultado["lugar"].isin(f_lugar)]
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        inicio_rango, fin_rango = rango_fechas
        resultado = resultado[
            (pd.to_datetime(resultado["fecha"]) >= pd.to_datetime(inicio_rango))
            & (pd.to_datetime(resultado["fecha"]) <= pd.to_datetime(fin_rango))
        ]
    if texto_libre:
        texto = texto_libre.lower()
        resultado = resultado[
            resultado["capacitador"].str.lower().str.contains(texto, na=False)
            | resultado["auxiliar"].str.lower().str.contains(texto, na=False)
            | resultado["lugar"].str.lower().str.contains(texto, na=False)
        ]

    st.write(f"**{len(resultado)}** registro(s) encontrado(s)")
    st.dataframe(resultado, width='stretch', hide_index=True)

    st.divider()
    st.subheader("Editar / eliminar un registro")

    if resultado.empty:
        st.info("No hay registros que coincidan con la búsqueda para editar.")
    else:
        id_seleccionado = st.selectbox("Selecciona el ID a editar", resultado["id"].tolist())
        registro = resultado[resultado["id"] == id_seleccionado].iloc[0]

        with st.form("form_edicion"):
            col1, col2, col3 = st.columns(3)
            with col1:
                e_tipo = campo_con_opciones("Tipo", valores_existentes(df, "tipo"), f"edit_tipo_{id_seleccionado}", registro["tipo"])
                e_fecha = st.date_input("Fecha", value=pd.to_datetime(registro["fecha"]).date(), key=f"edit_fecha_{id_seleccionado}")
                e_capacitador = campo_con_opciones("Capacitador", valores_existentes(df, "capacitador"), f"edit_capacitador_{id_seleccionado}", registro["capacitador"])
            with col2:
                e_auxiliar = campo_con_opciones("Auxiliar", ["NO APLICA"] + valores_existentes(df, "auxiliar"), f"edit_auxiliar_{id_seleccionado}", registro["auxiliar"])
                e_tipo_auxilio = campo_con_opciones("Tipo de auxilio", OPCIONES_TIPO_AUXILIO, f"edit_tipo_auxilio_{id_seleccionado}", registro["tipo_auxilio"])
                e_modalidad = campo_con_opciones("Modalidad", OPCIONES_MODALIDAD, f"edit_modalidad_{id_seleccionado}", registro["modalidad"])
            with col3:
                e_inicio = st.time_input("Hora de inicio", value=convertir_a_time(registro["inicio"]), key=f"edit_inicio_{id_seleccionado}")
                e_fin = st.time_input("Hora de fin", value=convertir_a_time(registro["fin"]), key=f"edit_fin_{id_seleccionado}")
                e_lugar = campo_con_opciones("Lugar", valores_existentes(df, "lugar"), f"edit_lugar_{id_seleccionado}", registro["lugar"])

            col4, col5 = st.columns(2)
            with col4:
                e_comunidad = st.radio(
                    "¿Es comunidad?", OPCIONES_SI_NO, horizontal=True,
                    index=OPCIONES_SI_NO.index(registro["es_comunidad"]) if registro["es_comunidad"] in OPCIONES_SI_NO else 0,
                    key=f"edit_comunidad_{id_seleccionado}",
                )
            with col5:
                e_asistentes = st.number_input("Asistentes", min_value=0, step=1, value=int(registro["asistentes"]), key=f"edit_asistentes_{id_seleccionado}")

            col_guardar, col_eliminar = st.columns(2)
            with col_guardar:
                actualizar = st.form_submit_button("💾 Guardar cambios", type="primary")
            with col_eliminar:
                borrar = st.form_submit_button("🗑️ Eliminar registro")

        if actualizar:
            datos = {
                "tipo": e_tipo,
                "fecha": e_fecha,
                "dia_semana": calcular_dia_semana(e_fecha),
                "capacitador": e_capacitador,
                "auxiliar": e_auxiliar,
                "tipo_auxilio": e_tipo_auxilio,
                "modalidad": e_modalidad,
                "inicio": e_inicio,
                "fin": e_fin,
                "lugar": e_lugar,
                "es_comunidad": e_comunidad,
                "asistentes": int(e_asistentes),
            }
            try:
                actualizar_registro(engine, int(id_seleccionado), datos)
                st.cache_data.clear()
                st.success("Registro actualizado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

        if borrar:
            try:
                eliminar_registro(engine, int(id_seleccionado))
                st.cache_data.clear()
                st.success("Registro eliminado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")