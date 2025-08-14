import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_csv import load_csv

# Carregar dados
@st.cache_data

def carregar_dados():
    df_final = load_csv(df_final)


# Gráfico 1
contagem_eletrico = df_final["eletrico"].value_counts().reset_index()
contagem_eletrico.columns = ["Tipo de ônibus", "Quantidade"]

mapeamento = {0: "Não elétrico", 1: "Elétrico", False: "Não elétrico", True: "Elétrico"}
contagem_eletrico["Tipo de ônibus"] = contagem_eletrico["Tipo de ônibus"].map(mapeamento)

fig1 = px.pie(
    contagem_eletrico,
    values="Quantidade",
    names="Tipo de ônibus",
    title="Proporção por tipo de ônibus",
    color="Tipo de ônibus",
    color_discrete_map={
        "Não elétrico": "#d53e4f",
        "Elétrico": "#99d594"
    },
    hole=0.5
)

fig1.update_traces(textinfo="percent+label", textposition="inside")
fig1.update_layout(
    legend_title="Tipo de ônibus:",
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1
    )
)

# Gráfico 2
onibus_eletricos = df_final[df_final["eletrico"] == True]
contagem_modelo = onibus_eletricos["modelo"].value_counts().reset_index()
contagem_modelo.columns = ["Modelo de ônibus", "Quantidade"]

fig2 = px.pie(
    contagem_modelo,
    values="Quantidade",
    names="Modelo de ônibus",
    title="Proporção de ônibus elétricos por modelo",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Tab20
)

fig2.update_traces(textinfo="percent+label", textposition="inside")
fig2.update_layout(
    legend_title="Modelo de ônibus:",
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1
    )
)

# Exibir lado a lado
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)


# Gráficos 3
df_final["momento_inicial"] = pd.to_datetime(df_final["momento_inicial"])
df_final["hora_min"] = df_final["momento_inicial"].dt.strftime("%H:%M")

df_eletricos = df_final[df_final["eletrico"] == True]
df_nao_eletricos = df_final[df_final["eletrico"] == False]

emissoes = df_nao_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes.columns = ["Horário do dia", "Emissões de CO₂ (kg)"]

emissoes_evitadas = df_eletricos.groupby("hora_min")["emissao_co2"].sum().cumsum().sort_index().reset_index()
emissoes_evitadas.columns = ["Horário do dia", "Emissões de CO₂ (kg)"]

fig1 = px.line(
    emissoes,
    x="Horário do dia",
    y="Emissões de CO₂ (kg)",
    markers=True,
    title="Emissões de CO₂ acumuladas ao longo do dia - ônibus não elétricos"
)
fig1.update_traces(line_color="#d53e4f", text=emissoes["Emissões de CO₂ (kg)"].round(4), textposition="top center")
fig1.update_layout(
    yaxis_title="Emissões de CO₂ (kg)",
    xaxis_title="Horário do dia",
    plot_bgcolor="white",
    yaxis=dict(showgrid=True, gridcolor="lightgray", gridwidth=0.5, griddash="dot"),
    xaxis=dict(showgrid=False)
)

# Gráfico 2
fig2 = px.line(
    emissoes_evitadas,
    x="Horário do dia",
    y="Emissões de CO₂ (kg)",
    markers=True,
    title="Emissões de CO₂ evitadas ao longo do dia - ônibus elétricos"
)
fig2.update_traces(line_color="#99d594", text=emissoes_evitadas["Emissões de CO₂ (kg)"].round(4), textposition="top center")
fig2.update_layout(
    yaxis_title="Emissões de CO₂ (kg)",
    xaxis_title="Horário do dia",
    plot_bgcolor="white",
    yaxis=dict(showgrid=True, gridcolor="lightgray", gridwidth=0.5, griddash="dot"),
    xaxis=dict(showgrid=False)
)

# Exibir lado a lado
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)