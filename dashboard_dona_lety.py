import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dona Lety - Reporte Ejecutivo",
    page_icon=None,
    layout="wide",
)

@st.cache_data
def cargar_datos():
    df = pd.read_excel("Doña Lety conquista Europa.xlsx", sheet_name="Pedidos")
    df["Ingreso_Total"] = df["Precio Unidad (incluye % distribuidor)"] * df["Cantidad"]
    df["Costo_Total"]   = df["Costo de producción"] * df["Cantidad"]
    df["Ganancia"]      = df["Ingreso_Total"] - df["Costo_Total"]
    df["Margen_%"]      = (df["Ganancia"] / df["Ingreso_Total"] * 100).round(2)
    df["Año"]           = df["Fecha Pedido"].dt.year
    df["Mes"]           = df["Fecha Pedido"].dt.month
    df["Trimestre"]     = df["Fecha Pedido"].dt.quarter
    df["Año-Trim"]      = df["Año"].astype(str) + "-Q" + df["Trimestre"].astype(str)
    return df

df_raw = cargar_datos()

COLORES_CAT  = {"Pasteles": "#e07b54", "Galletas": "#5b9e6e", "Gelatinas": "#5b86c2"}
COLORES_DIST = {"Rappi": "#f5a623", "DIDI Food": "#7b68ee", "Uber eats": "#50c878"}

# SIDEBAR
with st.sidebar:
    st.title("Dona Lety")
    st.caption("Campana: Regresando a Casa")
    st.divider()
    st.subheader("Filtros")

    anios_disp = sorted(df_raw["Año"].unique())
    anios_sel  = st.multiselect("Año", anios_disp, default=anios_disp)

    paises_disp = sorted(df_raw["País"].unique())
    paises_sel  = st.multiselect("Pais", paises_disp, default=paises_disp)

    cats_disp = sorted(df_raw["Categoría Producto"].unique())
    cats_sel  = st.multiselect("Categoria de Producto", cats_disp, default=cats_disp)

    dist_disp = sorted(df_raw["Distribuidor"].unique())
    dist_sel  = st.multiselect("Distribuidor", dist_disp, default=dist_disp)

    st.divider()
    st.caption("Datos: 2009 - 2012 | Europa")

df = df_raw[
    df_raw["Año"].isin(anios_sel) &
    df_raw["País"].isin(paises_sel) &
    df_raw["Categoría Producto"].isin(cats_sel) &
    df_raw["Distribuidor"].isin(dist_sel)
].copy()

if df.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros del panel lateral.")
    st.stop()

# ENCABEZADO
st.title("Reporte Ejecutivo - Dona Lety Conquista Europa")
st.markdown(
    "**Campana:** *Regresando a Casa* &nbsp;|&nbsp; "
    "**Objetivo:** Distribuir el presupuesto de mercadotecnia para la expansion americana "
    "con base en el desempeno historico en Europa."
)
st.divider()

# FILA 1 - KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ingreso Total",   f"EUR {df['Ingreso_Total'].sum()/1e6:.2f} M")
k2.metric("Ganancia Total",  f"EUR {df['Ganancia'].sum()/1e6:.2f} M")
k3.metric("Margen Promedio", f"{df['Margen_%'].mean():.1f}%")
k4.metric("Total Pedidos",   f"{len(df):,}")
k5.metric("Ticket Promedio", f"EUR {df['Ingreso_Total'].mean():,.0f}")
st.divider()

# FILA 2 - GEOGRAFIA + CATEGORIA + DISTRIBUIDOR
col_geo, col_pie, col_dist = st.columns([2, 1.2, 1.2])

with col_geo:
    st.subheader("Ingresos y Ganancia por Pais")
    pais_df = (
        df.groupby("País")
        .agg(
            Ingreso_M=("Ingreso_Total", lambda x: x.sum() / 1e6),
            Ganancia_M=("Ganancia",     lambda x: x.sum() / 1e6),
        )
        .reset_index()
        .sort_values("Ingreso_M", ascending=False)
    )
    fig_geo = go.Figure()
    fig_geo.add_trace(go.Bar(
        y=pais_df["País"], x=pais_df["Ingreso_M"],
        name="Ingresos (M EUR)", orientation="h",
        marker_color="#5b86c2",
        text=pais_df["Ingreso_M"].apply(lambda v: f"{v:.2f}M"),
        textposition="outside",
    ))
    fig_geo.add_trace(go.Bar(
        y=pais_df["País"], x=pais_df["Ganancia_M"],
        name="Ganancia (M EUR)", orientation="h",
        marker_color="#5b9e6e",
        text=pais_df["Ganancia_M"].apply(lambda v: f"{v:.2f}M"),
        textposition="outside",
    ))
    fig_geo.update_layout(
        barmode="group", height=400,
        margin=dict(l=0, r=70, t=10, b=0),
        legend=dict(orientation="h", y=-0.15),
        xaxis_title="Millones EUR",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_geo, use_container_width=True)

with col_pie:
    st.subheader("Ingresos por Categoria")
    cat_df = df.groupby("Categoría Producto")["Ingreso_Total"].sum().reset_index()
    cat_df.columns = ["Categoria", "Ingreso"]
    fig_pie = px.pie(
        cat_df, names="Categoria", values="Ingreso",
        color="Categoria", color_discrete_map=COLORES_CAT, hole=0.4,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_dist:
    st.subheader("Ingresos por Distribuidor")
    dist_df = (
        df.groupby("Distribuidor")["Ingreso_Total"].sum()
        .reset_index()
        .sort_values("Ingreso_Total", ascending=False)
    )
    dist_df["Ingreso_M"] = dist_df["Ingreso_Total"] / 1e6
    fig_dist = px.bar(
        dist_df, x="Distribuidor", y="Ingreso_M",
        color="Distribuidor", color_discrete_map=COLORES_DIST,
        text=dist_df["Ingreso_M"].apply(lambda v: f"{v:.1f}M"),
    )
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(
        height=380, showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="Millones EUR", xaxis_title="",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

# FILA 3 - TOP PRODUCTOS + ESTACIONALIDAD
col_prod, col_est = st.columns([1.2, 2])

with col_prod:
    st.subheader("Top Productos por Ingreso")
    n_top = st.slider("Numero de productos", 3, 17, 7, key="top_prod")
    top_prod = (
        df.groupby("Sub-Categoría de Producto")["Ingreso_Total"]
        .sum().reset_index()
        .rename(columns={"Sub-Categoría de Producto": "Producto", "Ingreso_Total": "Ingreso"})
        .sort_values("Ingreso", ascending=False)
        .head(n_top)
        .sort_values("Ingreso")
    )
    fig_prod = px.bar(
        top_prod, x="Ingreso", y="Producto", orientation="h",
        color="Ingreso", color_continuous_scale="Oranges",
        text=top_prod["Ingreso"].apply(lambda v: f"{v/1e6:.2f}M"),
    )
    fig_prod.update_traces(textposition="outside")
    fig_prod.update_layout(
        height=400, coloraxis_showscale=False,
        margin=dict(l=0, r=70, t=10, b=0),
        xaxis_title="Ingresos (EUR)", yaxis_title="",
    )
    st.plotly_chart(fig_prod, use_container_width=True)

with col_est:
    st.subheader("Estacionalidad de Ingresos")
    vista_temp = st.radio("Ver por", ["Mes", "Trimestre", "Año"], horizontal=True, key="vista_temp")

    if vista_temp == "Mes":
        temp_df = df.groupby(["Mes", "Categoría Producto"])["Ingreso_Total"].sum().reset_index()
        temp_df["Ingreso_M"] = temp_df["Ingreso_Total"] / 1e6
        meses = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                 7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        temp_df["Periodo"] = temp_df["Mes"].map(meses)
        temp_df["Orden"]   = temp_df["Mes"]
    elif vista_temp == "Trimestre":
        temp_df = df.groupby(["Año-Trim", "Categoría Producto"])["Ingreso_Total"].sum().reset_index()
        temp_df["Ingreso_M"] = temp_df["Ingreso_Total"] / 1e6
        temp_df["Periodo"]   = temp_df["Año-Trim"]
        temp_df["Orden"]     = temp_df["Año-Trim"]
    else:
        temp_df = df.groupby(["Año", "Categoría Producto"])["Ingreso_Total"].sum().reset_index()
        temp_df["Ingreso_M"] = temp_df["Ingreso_Total"] / 1e6
        temp_df["Periodo"]   = temp_df["Año"].astype(str)
        temp_df["Orden"]     = temp_df["Año"]

    temp_df = temp_df.sort_values("Orden")
    fig_est = px.line(
        temp_df, x="Periodo", y="Ingreso_M",
        color="Categoría Producto", color_discrete_map=COLORES_CAT,
        markers=True,
    )
    fig_est.update_layout(
        height=400, margin=dict(l=0, r=0, t=10, b=60),
        yaxis_title="Ingresos (M EUR)", xaxis_title="",
        legend=dict(title="Categoria", orientation="h", y=-0.25),
    )
    fig_est.update_xaxes(tickangle=-40)
    st.plotly_chart(fig_est, use_container_width=True)

st.divider()

# FILA 4 - HEATMAP + MARGEN
col_heat, col_margen = st.columns([2, 1.3])

with col_heat:
    st.subheader("Ingresos por Pais x Categoria")
    metrica_heat = st.selectbox(
        "Metrica",
        ["Ingreso Total (M EUR)", "Ganancia (M EUR)", "Pedidos", "Margen Promedio (%)"],
        key="metrica_heat",
    )
    if metrica_heat == "Ingreso Total (M EUR)":
        piv = df.pivot_table("Ingreso_Total", "País", "Categoría Producto", aggfunc="sum") / 1e6
        fmt = ".1f"
    elif metrica_heat == "Ganancia (M EUR)":
        piv = df.pivot_table("Ganancia", "País", "Categoría Producto", aggfunc="sum") / 1e6
        fmt = ".1f"
    elif metrica_heat == "Pedidos":
        piv = df.pivot_table("ID Pedido", "País", "Categoría Producto", aggfunc="count")
        fmt = ".0f"
    else:
        piv = df.pivot_table("Margen_%", "País", "Categoría Producto", aggfunc="mean")
        fmt = ".1f"

    # Ordenar filas por total descendente
    piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index]

    fig_heat = px.imshow(
        piv.round(2), text_auto=fmt,
        color_continuous_scale="YlOrRd", aspect="auto",
    )
    fig_heat.update_layout(
        height=420, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title=""),
        xaxis_title="", yaxis_title="",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_margen:
    st.subheader("Margen Promedio")
    tipo_margen = st.radio(
        "Agrupar por", ["Categoria", "Distribuidor", "Pais"],
        horizontal=True, key="tipo_margen",
    )
    grp_map = {"Categoria": "Categoría Producto", "Distribuidor": "Distribuidor", "Pais": "País"}
    col_map = {"Categoria": COLORES_CAT, "Distribuidor": COLORES_DIST, "Pais": None}

    grp_col   = grp_map[tipo_margen]
    color_map = col_map[tipo_margen]

    marg_df = (
        df.groupby(grp_col)["Margen_%"].mean()
        .reset_index()
        .rename(columns={grp_col: "Grupo", "Margen_%": "Margen"})
        .sort_values("Margen", ascending=False)
    )
    marg_df["Margen"] = marg_df["Margen"].round(1)

    fig_marg = px.bar(
        marg_df, x="Margen", y="Grupo", orientation="h",
        color="Grupo",
        color_discrete_map=color_map if color_map else {},
        text=marg_df["Margen"].apply(lambda v: f"{v:.1f}%"),
    )
    fig_marg.update_traces(textposition="outside")
    fig_marg.update_layout(
        height=420, showlegend=False,
        margin=dict(l=0, r=60, t=10, b=0),
        xaxis_title="Margen (%)", yaxis_title="",
        xaxis_range=[0, marg_df["Margen"].max() * 1.25],
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_marg, use_container_width=True)

st.divider()

# FILA 5 - TABLA EJECUTIVA
st.subheader("Tabla Ejecutiva de Detalle")
nivel = st.selectbox(
    "Ver resumen por",
    ["País", "Categoría Producto", "Sub-Categoría de Producto", "Distribuidor", "Año"],
    key="nivel_tabla",
)

tabla = (
    df.groupby(nivel)
    .agg(
        Pedidos=("ID Pedido",      "count"),
        Unidades=("Cantidad",      "sum"),
        Ingreso_M=("Ingreso_Total", lambda x: round(x.sum() / 1e6, 3)),
        Ganancia_M=("Ganancia",    lambda x: round(x.sum() / 1e6, 3)),
        Margen_Prom=("Margen_%",   lambda x: round(x.mean(), 1)),
        Ticket_Prom=("Ingreso_Total", lambda x: round(x.mean(), 0)),
    )
    .reset_index()
    .sort_values("Ingreso_M", ascending=False)
)

st.dataframe(
    tabla.style
        .background_gradient(subset=["Ingreso_M", "Ganancia_M"], cmap="Greens")
        .background_gradient(subset=["Margen_Prom"], cmap="Blues")
        .format({
            "Ingreso_M":   "{:.3f} M EUR",
            "Ganancia_M":  "{:.3f} M EUR",
            "Margen_Prom": "{:.1f}%",
            "Ticket_Prom": "EUR {:,.0f}",
            "Pedidos":     "{:,}",
            "Unidades":    "{:,}",
        }),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.caption(
    f"Fuente: Dona Lety conquista Europa.xlsx  |  "
    f"Registros analizados: {len(df):,} de {len(df_raw):,} totales  |  "
    "Periodo: 2009 - 2012"
)
