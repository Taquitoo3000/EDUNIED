import math
import pandas as pd
import streamlit as st
from datetime import datetime, date, time, timedelta

DIAS_SEMANA_ES = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
]
COORDENADAS = {
    'LEÓN':                          (21.1250, -101.6860),
    'CELAYA':                        (20.5234, -100.8157),
    'SAN MIGUEL DE ALLENDE':         (20.9144, -100.7450),
    'SALVATIERRA':                   (20.2134, -100.8802),
    'IRAPUATO':                      (20.6896, -101.3540),
    'YURIRIA':                       (20.2100, -101.1328),
    'SILAO':                         (20.9437, -101.4270),
    'DOLORES HIDALGO C.I.N.':        (21.1564, -100.9345),
    'DOLORES HIDALGO':               (21.1564, -100.9345),
    'VILLAGRÁN':                     (20.5153, -100.9972),
    'TARANDACUAO':                   (20.0000, -100.5167),
    'VALLE DE SANTIAGO':             (20.3928, -101.1917),
    'GUANAJUATO':                    (21.0190, -101.2574),
    'PUEBLO NUEVO':                  (20.5436, -101.3714),
    'SALAMANCA':                     (20.5706, -101.1975),
    'CORTAZAR':                      (20.4833, -100.9667),
    'APASEO EL GRANDE':              (20.5458, -100.6861),
    'ACÁMBARO':                      (20.0300, -100.7222),
    'COMONFORT':                     (20.7222, -100.7597),
    'SAN LUIS DE LA PAZ':            (21.2986, -100.5167),
    'MOROLEÓN':                      (20.1278, -101.1917),
    'SAN FELIPE':                    (21.4781, -101.2156),
    'SAN FRANCISCO DEL RINCÓN':      (21.0183, -101.8550),
    'SAN JOSÉ ITURBIDE':             (21.0014, -100.3842),
    'APASEO EL ALTO':                (20.4583, -100.6208),
    'XICHÚ':                         (21.3000, -100.0583),
    'CORONEO':                       (20.2000, -100.3667),
    'PÉNJAMO':                       (20.4314, -101.7228),
    'VICTORIA':                      (21.2111, -100.2139),
    'TARIMORO':                      (20.2889, -100.7583),
    'HUANÍMARO':                     (20.3683, -101.4997),
    'PURÍSIMA DEL RINCÓN':           (21.0344, -101.8700),
    'PURÍSIMA':                      (21.0344, -101.8700),
    'TIERRA BLANCA':                 (21.1000, -100.1583),
    'JERÉCUARO':                     (20.1556, -100.5083),
    'CUERÁMARO':                     (20.6250, -101.6736),
    'ABASOLO':                       (20.4494, -101.5303),
    'SANTIAGO MARAVATÍO':            (20.1739, -101.0000),
    'JUVENTINO ROSAS':               (20.6433, -100.9928),
    'SANTA CATARINA':                (21.1411, -100.0694),
    'ATARJEA':                       (21.2667,  -99.7167),
    'OCAMPO':                        (21.6472, -101.4792),
    'URIANGATO':                     (20.1400, -101.1717),
    'JARAL DEL PROGRESO':            (20.3714, -101.0611),
    'SAN DIEGO DE LA UNIÓN':         (21.4667, -100.8750),
    'DOCTOR MORA':                   (21.1411, -100.3194),
    'MANUEL DOBLADO':                (20.7289, -101.9525),
    'ROMITA':                        (20.8711, -101.5169),
}
ORIGEN = "LEÓN"

def valores_existentes(df, columna):
    """Lista de valores únicos ya usados en una columna, para poblar selectboxes."""
    if df is None or df.empty or columna not in df.columns:
        return []
    return sorted([v for v in df[columna].dropna().unique().tolist() if str(v).strip() != ""])


def campo_con_opciones(label, opciones, key, valor_actual=None):
    """
    Selectbox con las opciones existentes + 'Otro (escribir nuevo)'.
    Si el usuario elige 'Otro', muestra un text_input debajo.
    Devuelve el texto final elegido/escrito.
    """
    lista = list(opciones)
    if valor_actual and valor_actual not in lista:
        lista = [valor_actual] + lista

    indice_default = lista.index(valor_actual) if valor_actual in lista else 0
    seleccion = st.selectbox(label, lista, index=indice_default, key=f"{key}_sel")
    return seleccion


def calcular_dia_semana(fecha_valor):
    if fecha_valor is None:
        return None
    if isinstance(fecha_valor, (date, datetime)):
        return DIAS_SEMANA_ES[fecha_valor.weekday()]
    return None

def convertir_a_time(valor):
    """
    Normaliza a datetime.time sin importar cómo venga el valor:
    - ya es datetime.time -> se regresa igual
    - pandas/​datetime.timedelta (típico al leer una columna TIME de MySQL) -> se convierte
    - datetime/pd.Timestamp -> se toma solo la parte de hora
    - texto -> se intenta parsear
    - None/NaN -> time(0, 0) como valor por defecto seguro
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return time(0, 0)
    if isinstance(valor, time):
        return valor
    if isinstance(valor, (pd.Timedelta, timedelta)):
        segundos_totales = int(valor.total_seconds()) % (24 * 3600)
        horas, resto = divmod(segundos_totales, 3600)
        minutos, segundos = divmod(resto, 60)
        return time(horas, minutos, segundos)
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.time()
    try:
        return pd.to_datetime(str(valor)).time()
    except Exception:
        return time(0, 0)

def calcular_horas(inicio, fin):
    inicio = convertir_a_time(inicio)
    fin = convertir_a_time(fin)
    dt_inicio = datetime.combine(date.today(), inicio)
    dt_fin = datetime.combine(date.today(), fin)
    if dt_fin < dt_inicio:
        dt_fin += timedelta(days=1)
    return round((dt_fin - dt_inicio).total_seconds() / 3600, 2)

def _haversine_km(coord1: tuple, coord2: tuple) -> float:
    """Distancia en km en línea recta entre dos puntos (lat, lon)."""
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))

def _distancia_desde_origen(lugar) -> float:
    """Km desde León al lugar. Devuelve 0 si el lugar no está en COORDENADAS."""
    if pd.isna(lugar):
        return 0.0
    clave = str(lugar).strip().upper()
    if clave not in COORDENADAS:
        return 0.0
    return _haversine_km(COORDENADAS[ORIGEN], COORDENADAS[clave])

# ==================== ÍNDICE DE CARGA DE TRABAJO ====================

def calcular_indice_carga(df: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    """
    Calcula, por persona (capacitador o auxiliar), un índice de carga de
    trabajo 0-100 combinando: # sesiones, horas totales, asistentes totales,
    días distintos trabajados y km recorridos, cada uno normalizado contra
    el máximo observado y ponderado según `pesos`.

    Los km se calculan desde León; si una persona visita varios lugares el
    mismo día, solo cuenta la distancia al lugar más lejano de ese día.
    """

    columnas_salida = ["persona", "rol", "sesiones", "horas_totales",
                       "asistentes_totales", "dias_distintos",
                       "km_totales", "indice_carga"]
    if df.empty:
        return pd.DataFrame(columns=columnas_salida)
 
    df = df.copy()
    df["horas"] = df.apply(lambda r: calcular_horas(r["inicio"], r["fin"]), axis=1)
    df["km_lugar"] = df["lugar"].apply(_distancia_desde_origen)
 
    filas = []
    for rol, columna in [("capacitador", "capacitador"), ("auxiliar", "auxiliar")]:
        subset = df[df[columna].notna() & (df[columna].str.upper() != "NO APLICA")]
        agrupado = subset.groupby(columna).agg(
            sesiones=("id", "count"),
            horas_totales=("horas", "sum"),
            asistentes_totales=("asistentes", "sum"),
            dias_distintos=("fecha", "nunique"),
        )
        km = (
            subset.groupby([columna, "fecha"])["km_lugar"].max()
            .groupby(level=0).sum()
            .rename("km_totales")
        )
        agrupado = (
            agrupado.join(km)
            .reset_index()
            .rename(columns={columna: "persona"})
        )
        agrupado["rol"] = rol
        filas.append(agrupado)
 
    resultado = pd.concat(filas, ignore_index=True)
    if resultado.empty:
        return resultado
 
    for col in ["sesiones", "horas_totales", "asistentes_totales", "dias_distintos", "km_totales"]:
        maximo = resultado[col].max()
        resultado[f"{col}_norm"] = (resultado[col] / maximo * 100) if maximo > 0 else 0
 
    resultado["indice_carga"] = (
        resultado["sesiones_norm"] * pesos["sesiones"]
        + resultado["horas_totales_norm"] * pesos["horas"]
        + resultado["asistentes_totales_norm"] * pesos["asistentes"]
        + resultado["dias_distintos_norm"] * pesos["dias"]
        + resultado["km_totales_norm"] * pesos["km"]
    ) / sum(pesos.values())

    resultado["km_totales"] = resultado["km_totales"].round(1)
    resultado = resultado.sort_values("indice_carga", ascending=False)
    return resultado[columnas_salida]