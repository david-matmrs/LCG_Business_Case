import streamlit as st # type: ignore
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.express as px


def run_dashboard():
    
    # ======================
    # Logo y título
    # ======================
    
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, "images/LCG_logo.png")
    st.image(image_path, width=1500) 

    st.markdown(
        """
        <h1 style='text-align: center; color: #16a085; font-family: 'Montserrat', sans-serif; font-weight: bold;'>
        LCG Business Case Dashboard
        </h1>
        """,
    unsafe_allow_html=True) 

    # ============================
    # Cargar dataset
    # ============================

    # Cargar datos
    @st.cache_data

    def load_data():
        df = pd.read_csv("BD_LCG_2017_CN.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Trimestre"] = df["Fecha"].dt.to_period("Q").astype(str)
        return df

    df = load_data()

    st.title("Análisis de datos de ventas")

    # Función auxiliar para filtrar por año
    def filtrar_por_anio(df, anio_input):
        if anio_input == "2015":
            return df[df["Año"] == 2015]
        elif anio_input == "2016":
            return df[df["Año"] == 2016]
        else:
            return df

    st.header("Pareto ABC por Departamentos")
    anio1 = st.selectbox("Selecciona el año para análisis ABC por departamento:", ["Sin agrupar", "2015", "2016"], key="abc_depto")
    df1 = filtrar_por_anio(df, anio1)
    ventas_departamento = df1.groupby("Departamento - Clave")["Ventas Netas (USD)"].sum().sort_values(ascending=False)
    ventas_total = ventas_departamento.sum()
    ventas_acumuladas = ventas_departamento.cumsum()
    porcentaje_acumulado = ventas_acumuladas / ventas_total

    clasificacion = porcentaje_acumulado.apply(lambda x: "A" if x <= 0.8 else ("B" if x <= 0.95 else "C"))
    ventas_departamento_df = pd.DataFrame({
        "Departamento": ventas_departamento.index,
        "Ventas": ventas_departamento.values,
        "Clasificación": clasificacion.values
    })

    resumen_clasificacion = ventas_departamento_df.groupby("Clasificación").agg(
        Monto_Ventas=("Ventas", "sum"),
        Numero_Departamentos=("Departamento", "count")
    ).reindex(["A", "B", "C"])  # Para mostrar en orden A, B, C
    st.subheader("Resumen por clasificación (A, B, C)")
    st.write(resumen_clasificacion)

    st.header("Pareto ABC por Clientes")
    anio_clientes = st.selectbox("Selecciona el año para análisis ABC por cliente:", ["Sin agrupar", "2015", "2016"], key="abc_cliente_pareto")
    df_clientes = filtrar_por_anio(df, anio_clientes)
    ventas_clientes_abc = df_clientes.groupby("Número de cliente")["Ventas Netas (USD)"].sum().sort_values(ascending=False)
    ventas_total_clientes = ventas_clientes_abc.sum()
    ventas_acumuladas_clientes = ventas_clientes_abc.cumsum()
    porcentaje_acumulado_clientes = ventas_acumuladas_clientes / ventas_total_clientes

    clasificacion_clientes = porcentaje_acumulado_clientes.apply(lambda x: "A" if x <= 0.8 else ("B" if x <= 0.95 else "C"))
    ventas_clientes_df = pd.DataFrame({
        "Cliente": ventas_clientes_abc.index,
        "Ventas": ventas_clientes_abc.values,
        "Clasificación": clasificacion_clientes.values
    })

    resumen_clasificacion_clientes = ventas_clientes_df.groupby("Clasificación").agg(
        Monto_Ventas=("Ventas", "sum"),
        Numero_Clientes=("Cliente", "count")
    ).reindex(["A", "B", "C"])
    st.subheader("Resumen por clasificación de clientes (A, B, C)")
    st.write(resumen_clasificacion_clientes)
    st.subheader("Top 5 clientes que más compran")
    anio2 = st.selectbox("Selecciona el año:", ["Sin agrupar", "2015", "2016"], key="abc_clientes")
    df2 = filtrar_por_anio(df, anio2)
    ventas_clientes = df2.groupby("Número de cliente")["Ventas Netas (USD)"].sum().sort_values(ascending=False)
    clientes_top5 = ventas_clientes.head(5)
    st.write("Aquí se muestran los clientes con más participación en el total de ventas por no. de cliente.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.write(clientes_top5)

    with col2:
        custom_colors = ['#17a589', '#34495e', "#117a65", '#229954', "#d9e0e5", '#515a5a',]
        total_ventas = ventas_clientes.sum()
        top5_sum = clientes_top5.sum()
        otros = total_ventas - top5_sum
        pie_data = pd.DataFrame({
            "Cliente": list(clientes_top5.index) + ["Otros"],
            "Ventas": list(clientes_top5.values) + [otros]
        })
        fig = px.pie(pie_data, names="Cliente", values="Ventas", hole=0.3, color_discrete_sequence=custom_colors)
        fig.update_layout(showlegend=True, height=350, width=350)
        st.plotly_chart(fig)

    # Vendedor que le vende a más clientes
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vendedor con más clientes atendidos")
        anio3 = st.selectbox("Selecciona el año:", ["2015", "2016"], key="vendedor")
        df3 = filtrar_por_anio(df, anio3)
        vendedor_clientes = df3.groupby("Número de Vendedor")["Número de cliente"].nunique()
        vendedor_mas_clientes = vendedor_clientes.idxmax()
        numero_clientes = vendedor_clientes.max()
        st.write(f"Vendedor con más clientes: {int(vendedor_mas_clientes)}. \n \n Número de clientes: {numero_clientes}")

    with col2:
        if "vendedor_mas_clientes" in locals():
            df_vendedor = df3[df3["Número de Vendedor"] == vendedor_mas_clientes]
            clientes_por_mes = df_vendedor.groupby(["Año", "Mes"])["Número de cliente"].nunique().reset_index()
            meses_dict = {1: " Enero" , 2: " Febrero" , 3: " Marzo" , 4: " Abril" , 5: " Mayo" , 6: " Junio" , 7: " Julio" , 8: " Agosto" , 9: " Septiembre" , 10: " Octubre" , 11: " Noviembre" , 12: " Diciembre" }
            clientes_por_mes["Mes "] = clientes_por_mes["Mes"].map(meses_dict)
            fig = px.bar(
                clientes_por_mes,
                x="Mes ",
                y="Número de cliente",
                labels={"Mes ": "Mes ", "Número de cliente": "Clientes únicos "},
                title="Clientes únicos atendidos por mes",
                color_discrete_sequence=["#16a085"]
            )
            fig.update_layout(xaxis_tickangle=-45, height=350, width=700)
            st.plotly_chart(fig)
        else:
            st.write("No hay datos para mostrar la gráfica.")

    st.header("Análisis de tendencia de ventas")
    ventas_por_mes = df.groupby(["Año", "Mes"])["Ventas Netas (USD)"].sum().reset_index()
    ventas_por_mes["Mes_str"] = ventas_por_mes["Año"].astype(str) + "-" + ventas_por_mes["Mes"].astype(str).str.zfill(2)

    col1, col2 = st.columns(2)

    opciones_anio = ["Sin agrupar", 2015, 2016]
    with col1:
        st.subheader("Mes con más ventas")
        anio_max = st.selectbox("Selecciona el año:", opciones_anio, key="mes_max")
        if anio_max == "Sin agrupar":
            data = ventas_por_mes
        else:
            data = ventas_por_mes[ventas_por_mes["Año"] == anio_max]
        if not data.empty:
            mes_max = data.loc[data["Ventas Netas (USD)"].idxmax()]
            st.write(f"Mes número {mes_max['Mes']} con ${mes_max['Ventas Netas (USD)']:,.2f}")
        else:
            st.write("No hay datos para mostrar.")

    with col2:
        st.subheader("Mes con menos ventas")
        anio_min = st.selectbox("Selecciona el año:", opciones_anio, key="mes_min")
        if anio_min == "Sin agrupar":
            data = ventas_por_mes
        else:
            data = ventas_por_mes[ventas_por_mes["Año"] == anio_min]
        if not data.empty:
            mes_min = data.loc[data["Ventas Netas (USD)"].idxmin()]
            st.write(f"Mes número {mes_min['Mes']} con ${mes_min['Ventas Netas (USD)']:,.2f}")
        else:
            st.write("No hay datos para mostrar.")

    # Gráfica de barras coloreando el mes con más ventas y el mes con menos ventas
    st.subheader("Ventas mensuales destacando máximos y mínimos")
    # Selección de año para la gráfica
    anio_graf = st.selectbox("Selecciona el año:", opciones_anio, key="graf_bar")
    if anio_graf == "Sin agrupar":
        data_graf = ventas_por_mes.copy()
    else:
        data_graf = ventas_por_mes[ventas_por_mes["Año"] == anio_graf].copy()

    if not data_graf.empty:
        idx_max = data_graf["Ventas Netas (USD)"].idxmax()
        idx_min = data_graf["Ventas Netas (USD)"].idxmin()
        # Color por barra
        colors = []
        for idx, row in data_graf.iterrows(): # row me sirve para iterar sobre las filas y poner colores diferentes
            if idx == idx_max:
                colors.append("#16a085")  # Verde para máximo
            elif idx == idx_min:
                colors.append("red")      # Rojo para mínimo
            else:
                colors.append("gray")     # Gris para el resto

        fig_bar = px.bar(
            data_graf,
            x="Mes_str",
            y="Ventas Netas (USD)",
            title="Ventas mensuales",
        )
        # Asignar colores manualmente
        fig_bar.update_traces(marker_color=colors)
        fig_bar.update_layout(
            xaxis_title="Mes",
            yaxis_title="Ventas Netas (USD)",
            showlegend=False,
            height=400,
            width=800
        )
        st.plotly_chart(fig_bar)
    else:
        st.write("No hay datos para mostrar la gráfica.")

    st.subheader("Porcentaje de crecimiento en ventas anual")
    ventas_anuales = df.groupby("Año")["Ventas Netas (USD)"].sum()
    if 2015 in ventas_anuales and 2016 in ventas_anuales:
        crecimiento = ((ventas_anuales[2016] - ventas_anuales[2015]) / ventas_anuales[2015]) * 100
        st.write(f"Crecimiento de 2015 a 2016: {crecimiento:.2f}%")
    # Serie de tiempo: Ventas mensuales
    ventas_ts = ventas_por_mes.copy()
    ventas_ts["Fecha"] = pd.to_datetime(ventas_ts["Año"].astype(str) + "-" + ventas_ts["Mes"].astype(str).str.zfill(2) + "-01")
    ventas_ts = ventas_ts.sort_values("Fecha")

    # Identificación de tendencia (regresión lineal simple)
    ventas_ts["Mes_ordinal"] = np.arange(len(ventas_ts))
    X = ventas_ts[["Mes_ordinal"]]
    y = ventas_ts["Ventas Netas (USD)"]
    model = LinearRegression()
    model.fit(X, y)
    ventas_ts["Tendencia"] = model.predict(X)

    fig_trend = px.line(
        ventas_ts,
        x="Fecha",
        y=["Ventas Netas (USD)", "Tendencia"],
        labels={"value": "USD", "variable": "Serie"},
        title="Tendencia de ventas mensuales", 
        line_shape="spline", 
        markers=False
    )
    fig_trend.update_traces(
        line=dict(color="#16a085"), 
        selector=dict(name="Ventas Netas (USD)")
    )
    fig_trend.update_traces(
        line=dict(color="#d9e0e5"), 
        selector=dict(name="Tendencia")
    )
    fig_trend.update_layout(showlegend=False)
    st.plotly_chart(fig_trend)

    # Estacionalidad: Promedio por mes del año
    st.subheader("Estacionalidad: Promedio de ventas por mes")
    ventas_estacionalidad = ventas_ts.groupby(ventas_ts["Fecha"].dt.month)["Ventas Netas (USD)"].mean()
    meses_dict = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    ventas_estacionalidad.index = ventas_estacionalidad.index.map(meses_dict)

    # Colorear barras: máximo en verde, mínimo en rojo, resto en gris
    idx_max = ventas_estacionalidad.values.argmax()
    idx_min = ventas_estacionalidad.values.argmin()
    colors = []
    for i in range(len(ventas_estacionalidad)):
        if i == idx_max:
            colors.append("#16a085")  # Verde para máximo
        elif i == idx_min:
            colors.append("red")      # Rojo para mínimo
        else:
            colors.append("gray")     # Gris para el resto

    fig_est = px.bar(
        x=ventas_estacionalidad.index,
        y=ventas_estacionalidad.values,
        labels={"x": "Mes", "y": "Ventas promedio (USD)"},
        title="Estacionalidad: Ventas promedio por mes"
    )
    fig_est.update_traces(marker_color=colors)

    # Línea punteada con el promedio de todos los meses
    promedio_total = ventas_estacionalidad.mean()
    fig_est.add_hline(
        y=promedio_total,
        line_dash="dot",
        line_color="#d9e0e5",
        annotation_text=f"Promedio: ${promedio_total:,.2f}",
        annotation_position="top left",
        annotation_font_color="#d9e0e5"
    )

    st.plotly_chart(fig_est)

    # Análisis de crecimiento: tasa de crecimiento mensual promedio
    st.subheader("Crecimiento mensual promedio")
    ventas_ts["Crecimiento (%)"] = ventas_ts["Ventas Netas (USD)"].pct_change() * 100
    crecimiento_mensual_prom = ventas_ts["Crecimiento (%)"].mean()
    st.write(f"Crecimiento mensual promedio: {crecimiento_mensual_prom:.2f}%")

    # Colorear barras
    colors = []
    for val in ventas_ts["Crecimiento (%)"]:
        if pd.isna(val):
            colors.append("gray")
        elif val <= -50:
            colors.append("red")
        elif val >= 50:
            colors.append("#16a085")
        else:
            colors.append("gray")

    fig_crec = px.bar(
        ventas_ts,
        x="Fecha",
        y="Crecimiento (%)",
        title="Tasa de crecimiento mensual (%)"
    )
    fig_crec.update_traces(marker_color=colors)
    st.plotly_chart(fig_crec)


    st.header("Análisis de rentabilidad del portafolio")

    st.subheader("Rentabilidad por mes y año")
    anio_rent = st.selectbox("Selecciona el año:", sorted(df["Año"].unique()), key="anio_rent")
    meses_dict = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    meses_disp = sorted(df[df["Año"] == anio_rent]["Mes"].unique())
    mes_rent = st.selectbox("Selecciona el mes:", [meses_dict[m] for m in meses_disp], key="mes_rent")
    mes_num = [k for k, v in meses_dict.items() if v == mes_rent][0]
    df_mes = df[(df["Año"] == anio_rent) & (df["Mes"] == mes_num)]
    ventas = df_mes["Ventas Netas (USD)"].sum()
    costo = df_mes["Costo (USD)"].sum()
    rentabilidad = ((ventas - costo) / costo) * 100 if costo > 0 else None
    st.write(f"Rentabilidad en {mes_rent} {anio_rent}: {rentabilidad:.2f}%" if rentabilidad is not None else "Datos insuficientes")

    st.subheader("Trimestre con menor rentabilidad")
    anio4 = st.selectbox("Selecciona el año:", ["2015", "2016"], key="trimestre")
    df4 = filtrar_por_anio(df, anio4)
    rent_trimestre = df4.groupby("Trimestre").agg({"Ventas Netas (USD)": "sum", "Costo (USD)": "sum"})
    rent_trimestre = rent_trimestre[rent_trimestre["Costo (USD)"] > 0]
    rent_trimestre["Rentabilidad (%)"] = ((rent_trimestre["Ventas Netas (USD)"] - rent_trimestre["Costo (USD)"]) / rent_trimestre["Costo (USD)"]) * 100
    if not rent_trimestre.empty:
        peor_trim = rent_trimestre["Rentabilidad (%)"].idxmin()
        peor_valor = rent_trimestre["Rentabilidad (%)"].min()
        st.write(f"Trimestre más bajo: {peor_trim} con rentabilidad de {peor_valor:.2f}%")
        fig_trim = px.bar(
            rent_trimestre.reset_index(),
            x="Trimestre",
            y="Rentabilidad (%)",
            title="Rentabilidad por trimestre",
            color_discrete_sequence=["#16a085"]
        )
        st.plotly_chart(fig_trim)
    else:
        st.write("Datos insuficientes para calcular rentabilidad por trimestre")

    st.subheader("Cliente menos rentable")
    opciones_cliente = [2015, 2016]
    anio_cliente = st.selectbox("Selecciona el año:", opciones_cliente, key="cliente_menos_rentable")
    if anio_cliente == "Sin agrupar":
        df_cliente = df.copy()
    else:
        df_cliente = df[df["Año"] == anio_cliente]

    rent_clientes = df_cliente.groupby(["Número de cliente", "Año"]).agg({"Ventas Netas (USD)": "sum", "Costo (USD)": "sum"})
    rent_clientes = rent_clientes[rent_clientes["Costo (USD)"] > 0]
    rent_clientes["Rentabilidad"] = ((rent_clientes["Ventas Netas (USD)"] - rent_clientes["Costo (USD)"]) / rent_clientes["Costo (USD)"]) * 100
    if not rent_clientes.empty:
        idx_peor = rent_clientes["Rentabilidad"].idxmin()
        peor_cliente = idx_peor[0]
        peor_anio = idx_peor[1]
        peor_valor = rent_clientes.loc[idx_peor, "Rentabilidad"]
        st.write(f"Cliente: {peor_cliente}, Rentabilidad: {peor_valor:.2f}%")

        df_graf = df_cliente #df[df["Año"] == peor_anio]
        ventas_totales_mes = df_graf.groupby(["Año", "Mes"])["Ventas Netas (USD)"].sum().reset_index()
        ventas_cliente_mes = df_graf[df_graf["Número de cliente"] == peor_cliente].groupby(["Año", "Mes"])["Ventas Netas (USD)"].sum().reset_index()
        ventas_totales_mes["Mes_str"] = ventas_totales_mes["Año"].astype(str) + "-" + ventas_totales_mes["Mes"].astype(str).str.zfill(2)
        ventas_cliente_mes = ventas_totales_mes.merge(
            ventas_cliente_mes, on=["Año", "Mes"], how="left", suffixes=("", "_cliente")
        )
        ventas_cliente_mes["Ventas Netas (USD)_cliente"] = ventas_cliente_mes["Ventas Netas (USD)_cliente"].fillna(0)

        import plotly.graph_objects as go
        fig = go.Figure()
        # Barras de fondo: ventas totales
        fig.add_trace(go.Bar(
            x=ventas_cliente_mes["Mes_str"],
            y=ventas_cliente_mes["Ventas Netas (USD)"],
            name="Ventas totales",
            marker_color="gray"
        ))
        # Barras superpuestas: ventas del cliente menos rentable
        fig.add_trace(go.Bar(
            x=ventas_cliente_mes["Mes_str"],
            y=ventas_cliente_mes["Ventas Netas (USD)_cliente"],
            name=f"Ventas cliente {peor_cliente}",
            marker_color="red"
        ))
        fig.update_layout(
            barmode="overlay",
            title=f"Ventas mensuales del cliente menos rentable ({peor_cliente}) vs ventas totales",
            xaxis_title="Mes",
            yaxis_title="Ventas Netas (USD)",
            height=400,
            width=800, 
            showlegend=False
        )
        fig.update_traces(opacity=0.85)
        st.plotly_chart(fig)
    else:
        st.write("No hay datos suficientes para calcular rentabilidad por cliente")

    # Gráfica: ventas del cliente menos rentable vs ventas totales (excluyendo clientes en cuartiles 2, 3 y 4 de rentabilidad)

    if not rent_clientes.empty:
            # Calcular cuartiles de rentabilidad
        rentabilidades = rent_clientes["Rentabilidad"].sort_values()
        q1 = rentabilidades.quantile(0.25)
        # Filtrar clientes en el primer cuartil (los menos rentables)
        clientes_q1 = rent_clientes[rent_clientes["Rentabilidad"] <= q1].index.get_level_values(0).unique()
        # Filtrar datos solo para clientes en el primer cuartil
        df_q1 = df_cliente[df_cliente["Número de cliente"].isin(clientes_q1)]

            # Ventas totales por mes (solo clientes Q1)
        ventas_totales_mes_q1 = df_q1.groupby(["Año", "Mes"])["Ventas Netas (USD)"].sum().reset_index()
            # Ventas del cliente menos rentable por mes
        ventas_cliente_mes_q1 = df_q1[df_q1["Número de cliente"] == peor_cliente].groupby(["Año", "Mes"])["Ventas Netas (USD)"].sum().reset_index()
        ventas_totales_mes_q1["Mes_str"] = ventas_totales_mes_q1["Año"].astype(str) + "-" + ventas_totales_mes_q1["Mes"].astype(str).str.zfill(2)
        ventas_cliente_mes_q1 = ventas_totales_mes_q1.merge(
            ventas_cliente_mes_q1, on=["Año", "Mes"], how="left", suffixes=("", "_cliente")
        )
        ventas_cliente_mes_q1["Ventas Netas (USD)_cliente"] = ventas_cliente_mes_q1["Ventas Netas (USD)_cliente"].fillna(0)

        import plotly.graph_objects as go
        fig_q1 = go.Figure()
            # Barras de fondo: ventas totales Q1
        fig_q1.add_trace(go.Bar(
            x=ventas_cliente_mes_q1["Mes_str"],
            y=ventas_cliente_mes_q1["Ventas Netas (USD)"],
            name="Ventas totales Q1",
            marker_color="gray"
        ))
            # Barras superpuestas: ventas del cliente menos rentable
        fig_q1.add_trace(go.Bar(
            x=ventas_cliente_mes_q1["Mes_str"],
            y=ventas_cliente_mes_q1["Ventas Netas (USD)_cliente"],
            name=f"Ventas cliente {peor_cliente}",
            marker_color="red"
        ))
        st.write("Para una comparación visual más sencilla, se muestra a continuación la comparación del aporta a las ventas del cliente menos rentable. En este caso, solo comparando con el 25% de los clientes con menor aportación.")
        fig_q1.update_layout(
            barmode="overlay",
            title=f"Ventas mensuales cliente menos rentable (no. {int(peor_cliente)}) vs otros clientes poco rentables",
            xaxis_title="Mes",
            yaxis_title="Ventas Netas (USD)",
            height=400,
            width=800,
            showlegend=False
        )
        fig_q1.update_traces(opacity=0.85)
        st.plotly_chart(fig_q1)
    else:
        st.write("No hay datos suficientes para calcular la gráfica de cuartiles de rentabilidad.")
