import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from utils.load_csv import load_csv

# Layout
st.set_page_config(layout="wide")



# Container principal
with st.container(key='conteudoPrincipal'):
    with st.container(key='conteudoHeader'):
        st.markdown("<h1 style='text-align: center;'> Dashboard - Ônibus elétricos </h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.5rem; color: white;'> PMSP / Bloomberg </p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def carregar_dados():
    df_final = load_csv("df_final.csv")
    return df_final

df_final = carregar_dados()

# ----------------------
# GRÁFICO 1 - Tipo de ônibus
# ----------------------
st.markdown("## Sobre os ônibus")
df_final["eletrico"] = df_final["eletrico"].astype(bool)
contagem_eletrico = df_final["eletrico"].value_counts().reset_index()
contagem_eletrico.columns = ["Tipo de ônibus", "Quantidade"]

mapeamento = {False: "Não elétrico", True: "Elétrico"}
contagem_eletrico["Tipo de ônibus"] = contagem_eletrico["Tipo de ônibus"].map(mapeamento)

fig1 = px.pie(
    contagem_eletrico,
    values="Quantidade",
    names="Tipo de ônibus",
    title="Proporção por tipo de ônibus",
    color="Tipo de ônibus",
    color_discrete_map={
        "Não elétrico": "#d53e4f",
        "Elétrico": "#00cc96"
    },
    hole=0.5
)
fig1.update_traces(textinfo="none", hovertemplate="%{percent}")
fig1.update_layout(
    legend=dict(
        orientation="v",
        font=dict(size=14),
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05
    )
)

# ----------------------
# GRÁFICO 2 - Modelos
# ----------------------
onibus_eletricos = df_final[df_final["eletrico"]]
contagem_modelo = onibus_eletricos["modelo"].value_counts().reset_index()
contagem_modelo.columns = ["Modelo de ônibus", "Quantidade"]

fig2 = px.pie(
    contagem_modelo,
    values="Quantidade",
    names="Modelo de ônibus",
    title="Proporção de ônibus elétricos por modelo",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig2.update_traces(textinfo="none", hovertemplate="%{percent}")
fig2.update_layout(
    legend=dict(
        orientation="v",
        font=dict(size=14),
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.15
    )
)

# Exibir lado a lado
with st.expander("Clique para as visualizações"):
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

# ----------------------
# GRÁFICOS 3 - Emissões
# ----------------------
st.markdown("## Sobre as emissões de CO₂")
df_final["momento_inicial"] = pd.to_datetime(df_final["momento_inicial"])
df_final["hora_min"] = df_final["momento_inicial"].dt.strftime("%H:%M")

df_eletricos = df_final[df_final["eletrico"] == True]
df_nao_eletricos = df_final[df_final["eletrico"] == False]

emissoes = df_nao_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes.columns = ["Horário do dia", "Emissões de CO₂ (kg)"]

emissoes_evitadas = df_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes_evitadas.columns = ["Horário do dia", "Emissões de CO₂ (kg)"]

# 1 - Não elétricos
fig3 = px.line(
    emissoes,
    x="Horário do dia",
    y="Emissões de CO₂ (kg)",
    markers=True,
    title="Emissões de CO₂ acumuladas ao longo do dia - ônibus não elétricos"
)
fig3.update_traces(line_color="#d53e4f", hovertemplate="Emissões: %{y:.5f} kg<extra></extra>")
fig3.update_layout(plot_bgcolor="white")

# 2 - Elétricos
fig4 = px.line(
    emissoes_evitadas,
    x="Horário do dia",
    y="Emissões de CO₂ (kg)",
    markers=True,
    title="Emissões de CO₂ evitadas ao longo do dia - ônibus elétricos"
)
fig4.update_traces(line_color="#00cc96", hovertemplate="Emissões: %{y:.5f} kg<extra></extra>")
fig4.update_layout(plot_bgcolor="white")

# Exibir lado a lado
with st.expander("Clique para as visualizações"):
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig4, use_container_width=True)

# ----------------------
# MAPA
# ----------------------
import time



df_trips = pd.read_csv('trips_layer.csv')
df_trips.dtypes

df_trips = df_trips[['coordinates', 'timestamps']]
df_trips['coordinates'] = df_trips['coordinates'].apply(lambda x: eval(x))
df_trips['timestamps'] = df_trips['timestamps'].apply(lambda x: eval(x))

df_trips.dtypes

st.markdown("## Mapa interativo")

st.title("Animação TripsLayer - Ônibus")

# Configurações iniciais
max_time = max(df_trips['timestamps'].apply(max))
trail_length = 120  # segundos visíveis atrás do ponto atual
time_step = 60      # avanço de cada frame (segundos)
frame_delay = 2   # atraso entre frames (segundos)

# Placeholder para atualizar o gráfico
map_placeholder = st.empty()

# Variável de controle do tempo
current_time = 0


while current_time <= max_time:
    # Camada TripsLayer
    trips_layer = pdk.Layer(
        "TripsLayer",
        data=df_trips,
        get_path="coordinates",
        get_timestamps="timestamps",
        get_color=[255, 0, 0],  # vermelho para todos
        opacity=0.8,
        width_min_pixels=5,
        rounded=True,
        trail_length=trail_length,
        current_time=current_time
    )

    # Estado inicial da visão
    view_state = pdk.ViewState(
        latitude=-23.55,
        longitude=-46.57,
        zoom=11,
        pitch=45
    )

    # Cria o Deck
    r = pdk.Deck(layers=[trips_layer], initial_view_state=view_state)

    # Atualiza o gráfico no Streamlit
    map_placeholder.pydeck_chart(r)

    # Avança o tempo
    current_time += time_step
    time.sleep(frame_delay)

# ----------------------
# CSS - Header e Footer
# ----------------------
st.markdown(f"""
<style>
    .footer {{
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: gray;
        text-align: center;
        padding: 10px;
        font-size: medium;
    }}
    .footer img {{
        height: 30px;
        vertical-align: middle;
        margin-right: 10px;
    }}
    .stMainBlockContainer {{
        padding-left: 0;
    }}
    .st-key-conteudoHeader {{
        position: fixed;
        left: 6rem;
        top: 3rem;
        background-color: #303C30;
        z-index: 4;
        padding: 1rem;
        width: calc(100% - 12rem);
    }}
    .st-key-conteudoPrincipal {{
        padding: 0 6rem;
    }}
</style>
<div class="footer">
    <img src="https://prefeitura.sp.gov.br/documents/34276/25188012/logo_PrefSP__horizontal_fundo+claro+%281%29.png">
    Copyleft 2025 | Prefeitura de São Paulo © 2025
</div>
""", unsafe_allow_html=True)