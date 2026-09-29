import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from functions.calculos import calcular_indice_carga, COORDENADAS

# ---------------------- PALETA ----------------------

MORADO_OSCURO = "#7E00D4"
MORADO_MEDIO = "#8055AB"
MORADO_CLARO = "#e9c7ff"
GRIS_TEXTO = "#4a4a4a"

ESCALA_MORADA = ["#ff85ff", "#ff39f5", "#ea00ff", "#D400FF", "#B700FF", "#9900ff"]

PLANTILLA_PLOTLY = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Century Gothic, Montserrat, Arial, sans-serif", color=GRIS_TEXTO),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[MORADO_OSCURO, MORADO_MEDIO, "#b366ff", "#5c0099", "#d9b3ff"],
        margin=dict(t=40, l=10, r=10, b=10),
    )
)

# ------------------------------------------------------


def _kpi_con_tendencia(df, columna_fecha="fecha"):
    """
    Calcula sesiones/asistentes del mes actual vs el mes anterior,
    y arma 4 indicadores tipo 'gauge/delta' con Plotly (más vistosos
    que st.metric plano).
    """
    df = df.copy()
    df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    hoy = df[columna_fecha].max()
    mes_actual = hoy.to_period("M")
    mes_anterior = mes_actual - 1

    actual = df[df[columna_fecha].dt.to_period("M") == mes_actual]
    anterior = df[df[columna_fecha].dt.to_period("M") == mes_anterior]

    metricas = [
        ("Sesiones este mes", len(actual), len(anterior)),
        ("Asistentes este mes", int(actual["asistentes"].sum()), int(anterior["asistentes"].sum())),
        ("Capacitadores activos", actual["capacitador"].nunique(), anterior["capacitador"].nunique()),
        ("Sesiones en comunidad", int((actual["es_comunidad"].str.upper() == "SI").sum()),
         int((anterior["es_comunidad"].str.upper() == "SI").sum())),
    ]

    columnas = st.columns(4)
    for col, (titulo, valor, valor_previo) in zip(columnas, metricas):
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=valor,
            number={"font": {"size": 40, "color": MORADO_OSCURO}},
            delta={
                "reference": valor_previo,
                "relative": False,
                "increasing": {"color": "#1fa055"},
                "decreasing": {"color": "#d64545"},
            },
            title={"text": titulo, "font": {"size": 13, "color": "#888"}},
        ))
        fig.update_layout(template=PLANTILLA_PLOTLY, height=140, margin=dict(t=30, b=0, l=10, r=10))
        col.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render(df: pd.DataFrame):
    st.subheader("Panorama general")

    if df.empty:
        st.info("Aún no hay datos para mostrar estadísticas.")
        return

    _kpi_con_tendencia(df)

    st.divider()

    # ---------- SESIONES POR CAPACITADOR + MODALIDAD ----------
    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.markdown("**Sesiones por capacitador**")
        conteo = df["capacitador"].value_counts().sort_values(ascending=True)
        fig = px.bar(
            conteo, x=conteo.values, y=conteo.index, orientation="h",
            color=conteo.values, color_continuous_scale=ESCALA_MORADA,
            labels={"x": "Sesiones", "y": ""},
        )
        fig.update_layout(template=PLANTILLA_PLOTLY, showlegend=False, coloraxis_showscale=False, height=420)
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown("**Sesiones por modalidad**")
        conteo_mod = df["modalidad"].value_counts()
        fig = px.pie(
            conteo_mod, values=conteo_mod.values, names=conteo_mod.index,
            hole=0.55, color_discrete_sequence=[MORADO_OSCURO, MORADO_MEDIO, "#d9b3ff", "#5c0099"],
        )
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        fig.update_layout(template=PLANTILLA_PLOTLY, showlegend=False, height=420)
        st.plotly_chart(fig, width='stretch')

    # ---------- ASISTENTES POR TIPO + TENDENCIA MENSUAL ----------
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("**Asistentes por tipo de actividad**")
        agrupado = df.groupby("tipo")["asistentes"].sum().sort_values(ascending=False)
        fig = px.bar(
            agrupado, x=agrupado.index, y=agrupado.values,
            color=agrupado.values, color_continuous_scale=ESCALA_MORADA,
            labels={"x": "", "y": "Asistentes"},
        )
        fig.update_layout(template=PLANTILLA_PLOTLY, showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, width='stretch')

    with c4:
        st.markdown("**Tendencia de sesiones por mes**")
        df_fecha = df.copy()
        df_fecha["fecha"] = pd.to_datetime(df_fecha["fecha"])
        df_fecha["mes"] = df_fecha["fecha"].dt.to_period("M").astype(str)
        serie = df_fecha["mes"].value_counts().sort_index()
        fig = go.Figure(go.Scatter(
            x=serie.index, y=serie.values, mode="lines+markers",
            line=dict(color=MORADO_OSCURO, width=3, shape="spline"),
            marker=dict(size=7, color=MORADO_OSCURO),
            fill="tozeroy", fillcolor="rgba(126,0,212,0.12)",
        ))
        fig.update_layout(template=PLANTILLA_PLOTLY, height=380, xaxis_title="", yaxis_title="Sesiones")
        st.plotly_chart(fig, width='stretch')

    # ---------- MAPA DE COBERTURA ----------
    st.divider()
    st.markdown("### Cobertura geográfica")

    resumen_lugar = df.groupby("lugar").agg(
        sesiones=("id", "count"),
        asistentes=("asistentes", "sum"),
    ).reset_index()
    resumen_lugar["lat"] = resumen_lugar["lugar"].map(lambda x: COORDENADAS.get(x, (None, None))[0])
    resumen_lugar["lon"] = resumen_lugar["lugar"].map(lambda x: COORDENADAS.get(x, (None, None))[1])

    sin_coordenadas = resumen_lugar[resumen_lugar["lat"].isna()]["lugar"].tolist()
    resumen_mapa = resumen_lugar.dropna(subset=["lat", "lon"])

    if resumen_mapa.empty:
        st.info(
            "Ningún lugar de tus registros hace match con `COORDENADAS`. "
            "Revisa que los nombres en `functions/geo.py` sean idénticos a los de la columna `lugar`."
        )
    else:
        fig = px.scatter_mapbox(
            resumen_mapa, lat="lat", lon="lon",
            size="sesiones", color="asistentes",
            hover_name="lugar",
            hover_data={"lat": False, "lon": False, "sesiones": True, "asistentes": True},
            color_continuous_scale=ESCALA_MORADA,
            size_max=45, zoom=7.2,
            mapbox_style="carto-positron",
        )
        fig.update_layout(template=PLANTILLA_PLOTLY, height=480, margin=dict(t=10, l=0, r=0, b=0))
        st.plotly_chart(fig, width='stretch')

        if sin_coordenadas:
            st.caption(
                f"⚠️ Sin coordenadas para: {', '.join(sin_coordenadas)}. "
                "Solicita a soporte con UNIED."
            )

    # ---------- ÍNDICE DE CARGA DE TRABAJO ----------
    st.divider()
    st.markdown("### Índice de carga de trabajo por persona")
    st.caption(
        "Combina # de sesiones, horas totales, asistentes atendidos y días "
        "distintos trabajados. Ajusta la importancia de cada factor:"
    )

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    peso_sesiones = col_p1.slider("Peso: # sesiones", 0.0, 3.0, 1.0, 0.1)
    peso_horas = col_p2.slider("Peso: horas totales", 0.0, 3.0, 1.0, 0.1)
    peso_asistentes = col_p3.slider("Peso: asistentes", 0.0, 3.0, 1.0, 0.1)
    peso_dias = col_p4.slider("Peso: días distintos", 0.0, 3.0, 1.0, 0.1)

    pesos = {
        "sesiones": peso_sesiones,
        "horas": peso_horas,
        "asistentes": peso_asistentes,
        "dias": peso_dias,
    }

    indice_df = calcular_indice_carga(df, pesos)

    if indice_df.empty:
        st.info("No hay suficientes datos para calcular el índice.")
        return

    top15 = indice_df.head(15).sort_values("indice_carga", ascending=True)
    fig = px.bar(
        top15, x="indice_carga", y="persona", orientation="h",
        color="indice_carga", color_continuous_scale=ESCALA_MORADA,
        text=top15["indice_carga"].round(1),
        labels={"indice_carga": "Índice de carga", "persona": ""},
        hover_data={"rol": True, "sesiones": True, "horas_totales": ":.1f", "asistentes_totales": True},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(template=PLANTILLA_PLOTLY, showlegend=False, coloraxis_showscale=False, height=460)
    st.plotly_chart(fig, width='stretch')

    st.markdown("**Detalle completo**")
    st.dataframe(
        indice_df.style.format({
            "horas_totales": "{:.1f}",
            "asistentes_totales": "{:.0f}",
            "indice_carga": "{:.1f}",
        }),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Descargar índice como CSV",
        indice_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="indice_carga_trabajo.csv",
        mime="text/csv",
        icon=":material/download:",
    )