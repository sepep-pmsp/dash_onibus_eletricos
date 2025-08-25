import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import time
import numpy as np
from streamlit_mermaid import st_mermaid
from utils.load_csv import load_csv
from utils.load_shp import load_shp



# Layout
st.set_page_config(layout="wide")



# Sidebar
with st.sidebar:
    st.markdown("<h3 style='color: black;'>Sobre</h3>", unsafe_allow_html=True)

    st.markdown("""<div style = 'text-align: justify; color: black;' >
                    Este dashboard faz parte do projeto da Prefeitura Municipal de São Paulo com a Bloomberg.
                    As visualizações apresentam informações sobre o transporte público a ônibus como frotas, trajetos e emissões de poluentes.
                    </div> <br>""",
                unsafe_allow_html=True)

    with st.expander("Metodologia"):
        st_mermaid("""flowchart TD
                   A[Extração dos limites<br/>administrativos dos distritos da cidade] --> B[Simulação dos dados<br/>da API do Olho Vivo]
                   B --> C[Cálculo das emissões de poluentes<br/>e distância percorrida por ônibus]
                   C --> D[Agregação dos dados por distrito]
                   D --> E[Visualização dos dados]
                   E --> F[Elaboração do dashboard interativo]""")

    with st.expander("Fonte"):
        st.markdown("""<div style = 'text-align: justify; color: black;' >
                    SPTrans - API do Olho Vivo, 2025.
                    </div> <br>""",
                    unsafe_allow_html=True)



# CSS para Header e Footer
st.markdown("""
<style>
    /* HEADER FIXO */
    .custom-header {
        position: fixed;
        top: 2.5rem;
        left: 0;
        width: 100%;
        background-color: #F1EBDD;
        z-index: 1000;
        padding: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        text-align: center;
    }

    /* Compensar espaço do header no conteúdo */
    .main-content {
        padding-top: 6rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* FOOTER FIXO */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #F1EBDD;
        color: black;
        text-align: center;
        padding: 10px;
        font-size: medium;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    .footer img {
        height: 30px;
        vertical-align: middle;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)



# Header
st.markdown("""
<div class="custom-header">
    <h1 style='color: black; margin: 0;'>Dashboard - Protótipo</h1>
    <p style='font-size: 1.5rem; color: black; margin: 0;'>PMSP / Bloomberg</p>
</div>
""", unsafe_allow_html=True)



st.markdown("<br>", unsafe_allow_html=True)



# Conteúdo
st.markdown('<div class="main-content">', unsafe_allow_html=True)



# Carregar dados
@st.cache_data
def carregar_dados():
    df_final = load_csv("df_final.csv")
    df_trips = load_csv("df_trips.csv")
    distritos_final = load_shp("distritos_final.shp")
    return df_final, df_trips, distritos_final

df_final, df_trips, distritos_final = carregar_dados()



# ----- GRÁFICOS 1 -----
st.markdown("## Sobre os ônibus")


# Tipo de ônibus
df_final["eletrico"] = df_final["eletrico"].astype(bool)
contagem_eletrico = df_final["eletrico"].value_counts().reset_index()
contagem_eletrico.columns = ["Tipo de ônibus", "Quantidade"]
mapeamento = {False: "Não elétrico", True: "Elétrico"}
contagem_eletrico["Tipo de ônibus"] = contagem_eletrico["Tipo de ônibus"].map(mapeamento)
total_onibus = df_final["id_onibus"].nunique()

fig1 = px.pie(
    contagem_eletrico,
    values="Quantidade",
    names="Tipo de ônibus",
    title="Distribuição por tipo de ônibus",
    color="Tipo de ônibus",
    color_discrete_map={
        "Não elétrico": "#d53e4f",
        "Elétrico": "#00cc96"
    },
    hole=0.5
)
fig1.update_traces(textinfo="none", hovertemplate="%{percent}")
fig1.add_annotation(text=f"<b>Total:<br>{total_onibus}</b>", x=0.5, y=0.5, font=dict(size=20, color="black"), showarrow=False)
fig1.update_layout(legend=dict(orientation="v", font=dict(size=14, color = "black"), yanchor="middle", y=0.5, xanchor="left", x=1.05), 
                   hoverlabel=dict(font=dict(color="black"), bgcolor="white"))


# Modelo de ônibus
onibus_eletricos = df_final[df_final["eletrico"]]
contagem_modelo = onibus_eletricos["modelo"].value_counts().reset_index()
contagem_modelo.columns = ["Modelo de ônibus", "Quantidade"]
total_onibus_eletricos = onibus_eletricos["id_onibus"].nunique()

fig2 = px.pie(
    contagem_modelo,
    values="Quantidade",
    names="Modelo de ônibus",
    title="Distribuição de ônibus elétricos por modelo de ônibus",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig2.update_traces(textinfo="none", hovertemplate="%{percent}")
fig2.add_annotation(text=f"<b>Total:<br>{total_onibus_eletricos}</b>", x=0.5, y=0.5, font=dict(size=20, color="black"), showarrow=False)
fig2.update_layout(legend=dict(orientation="v", font=dict(size=14, color = "black"), yanchor="middle", y=0.5, xanchor="left", x=1.15), 
                   hoverlabel=dict(font=dict(color="black"), bgcolor="white"))

with st.expander("Clique para as visualizações"):
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)



st.markdown("<br>", unsafe_allow_html=True)



# ----- GRÁFICOS 2 -----
st.markdown("## Sobre as emissões de CO₂")
df_final["momento_inicial"] = pd.to_datetime(df_final["momento_inicial"])
df_final["hora_min"] = df_final["momento_inicial"].dt.strftime("%H:%M")
df_eletricos = df_final[df_final["eletrico"] == True]
df_nao_eletricos = df_final[df_final["eletrico"] == False]

emissoes = df_nao_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes.columns = ["Horário do dia", "Emissões de CO₂ (?)"]

emissoes_evitadas = df_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes_evitadas.columns = ["Horário do dia", "Emissões de CO₂ (?)"]


# Emissões acumuladas
fig3 = px.line(emissoes, x="Horário do dia", y="Emissões de CO₂ (?)", markers=True,
               title="Emissões de CO₂ acumuladas ao longo do dia - ônibus não elétricos")
fig3.update_traces(line_color="#d53e4f", hovertemplate="Emissões: %{y:.5f} (?)<extra></extra>",
                   hoverlabel=dict(font_color="black", bgcolor="white"))
fig3.update_layout(plot_bgcolor="white",
                   xaxis=dict(title_font_color="black", tickfont_color="black"),
                   yaxis=dict(title_font_color="black", tickfont_color="black"))


# Emissões evitadas
fig4 = px.line(emissoes_evitadas, x="Horário do dia", y="Emissões de CO₂ (?)", markers=True,
               title="Emissões de CO₂ evitadas ao longo do dia - ônibus elétricos")
fig4.update_traces(line_color="#00cc96", hovertemplate="Emissões: %{y:.5f} (?)<extra></extra>",
                   hoverlabel=dict(font_color="black", bgcolor="white"))
fig4.update_layout(plot_bgcolor="white",
                   xaxis=dict(title_font_color="black", tickfont_color="black"),
                   yaxis=dict(title_font_color="black", tickfont_color="black"))

with st.expander("Clique para as visualizações"):
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig3, use_container_width=True)
    col2.plotly_chart(fig4, use_container_width=True)



st.markdown("<br>", unsafe_allow_html=True)



# ----- MAPAS POR DISTRITO -----
st.markdown("## Mapas coropléticos por distrito")

distritos_final["emissao_nao_eletricos"] = np.where(
    distritos_final["eletrico"] == "False",
    distritos_final["emissao_co"],
    0
)

distritos_final["emissao_eletricos"] = np.where(
    distritos_final["eletrico"] == "True",
    distritos_final["emissao_co"],
    0
)

distritos_final = distritos_final.to_crs(epsg=4326)

abas = st.tabs([
    "Distância percorrida", 
    "Emissão de CO₂ - ônibus não elétricos", 
    "Emissão de CO₂ evitada - ônibus elétricos"
])

custom_cols = ["nm_distrit"]


# Distância
with abas[0]:
    with st.expander("Clique para a visualização"):
        fig_dist = px.choropleth_mapbox(
            distritos_final,
            geojson=distritos_final.geometry.__geo_interface__,
            locations=distritos_final.index,
            color="distancia",
            color_continuous_scale="Blues",
            range_color=[
                distritos_final["distancia"].min(),
                distritos_final["distancia"].max()
            ],
            mapbox_style="carto-positron",
            center={"lat": -23.7, "lon": -46.63},
            zoom=9,
            opacity=0.8,
            custom_data=custom_cols + ["distancia"]
        )
        fig_dist.update_traces(
            hovertemplate="<b>Distrito</b>: %{customdata[0]}<br>Distância: %{customdata[1]:.0f} (?)<extra></extra>",
            hoverlabel=dict(font=dict(color="black"), bgcolor="white"
        ))
        fig_dist.update_coloraxes(colorbar_title="Distância (?)", colorbar_title_side="right",
                                  colorbar_title_font=dict(color="black"),
                                  colorbar_tickfont=dict(color="black"))
        fig_dist.update_layout(margin={"r":300,"t":0,"l":300,"b":0}, height=600)
        st.plotly_chart(fig_dist, use_container_width=True)


# Emissão não elétricos
with abas[1]:
    with st.expander("Clique para a visualização"):
        fig_nao = px.choropleth_mapbox(
            distritos_final,
            geojson=distritos_final.geometry.__geo_interface__,
            locations=distritos_final.index,
            color="emissao_nao_eletricos",
            color_continuous_scale="Reds",
            range_color=[
                distritos_final["emissao_nao_eletricos"].min(),
                distritos_final["emissao_nao_eletricos"].max()
            ],
            mapbox_style="carto-positron",
            center={"lat": -23.7, "lon": -46.63},
            zoom=9,
            opacity=0.8,
            custom_data=custom_cols + ["emissao_nao_eletricos"]
        )
        fig_nao.update_traces(
            hovertemplate="<b>Distrito</b>: %{customdata[0]}<br>Emissão: %{customdata[1]:,.5f} (?)<extra></extra>",
            hoverlabel=dict(font=dict(color="black"), bgcolor="white"
        ))
        fig_nao.update_coloraxes(colorbar_title="Emissão de CO₂ (?)", colorbar_title_side="right",
                                 colorbar_title_font=dict(color="black"),
                                 colorbar_tickfont=dict(color="black"))
        fig_nao.update_layout(margin={"r":300,"t":0,"l":300,"b":0}, height=600)
        st.plotly_chart(fig_nao, use_container_width=True)


# Emissão elétricos
with abas[2]:
    with st.expander("Clique para a visualização"):
        fig_ele = px.choropleth_mapbox(
            distritos_final,
            geojson=distritos_final.geometry.__geo_interface__,
            locations=distritos_final.index,
            color="emissao_eletricos",
            color_continuous_scale="Greens",
            range_color=[
                distritos_final["emissao_eletricos"].min(),
                distritos_final["emissao_eletricos"].max()
            ],
            mapbox_style="carto-positron",
            center={"lat": -23.7, "lon": -46.63},
            zoom=9,
            opacity=0.8,
            custom_data=custom_cols + ["emissao_eletricos"]
        )
        fig_ele.update_traces(
            hovertemplate="<b>Distrito</b>: %{customdata[0]}<br>Emissão evitada: %{customdata[1]:,.5f} (?)<extra></extra>",
            hoverlabel=dict(font=dict(color="black"), bgcolor="white"
        ))
        fig_ele.update_coloraxes(colorbar_title="Emissão de CO₂ evitada (?)", colorbar_title_side="right",
                                 colorbar_title_font=dict(color="black"),
                                 colorbar_tickfont=dict(color="black"))
        fig_ele.update_layout(margin={"r":300,"t":0,"l":300,"b":0}, height=600)
        st.plotly_chart(fig_ele, use_container_width=True)



st.markdown("<br>", unsafe_allow_html=True)



# ----- MAPA TRAJETOS -----
st.markdown("## Mapa de trajeto dos ônibus")
df_trips = df_trips[['coordinates', 'timestamps']]
df_trips['coordinates'] = df_trips['coordinates'].apply(lambda x: eval(x))
df_trips['timestamps'] = df_trips['timestamps'].apply(lambda x: eval(x))

max_time = max(df_trips['timestamps'].apply(max))
trail_length = 800
time_step = 80
frame_delay = 2

col_left, col_center, col_right = st.columns([1, 5, 1]) 
with col_center:
    map_placeholder = st.empty()
    current_time = 0
    while current_time <= max_time:
        trips_layer = pdk.Layer(
            "TripsLayer",
            data=df_trips,
            get_path="coordinates",
            get_timestamps="timestamps",
            get_color=[255, 0, 0],
            opacity=0.8,
            width_min_pixels=5,
            rounded=True,
            trail_length=trail_length,
            current_time=current_time,
        )
        view_state = pdk.ViewState(latitude=-23.6, longitude=-46.63, zoom=11, pitch=45)
        r = pdk.Deck(layers=[trips_layer], initial_view_state=view_state)
        map_placeholder.pydeck_chart(r, height=600)
        current_time += time_step
        time.sleep(frame_delay)



st.markdown('</div>', unsafe_allow_html=True)



# Footer
st.markdown("""
<div class="footer">
    <img src="https://prefeitura.sp.gov.br/documents/34276/25188012/logo_PrefSP__horizontal_fundo+claro+%281%29.png">
    Copyleft 2025 | Prefeitura de São Paulo © 2025
</div>
""", unsafe_allow_html=True)