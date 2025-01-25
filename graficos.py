import pandas as pd
import plotly.express as px
import streamlit as st
from observacao import get_markdown
from config_page import config_page

# Configuração da página deve ser o primeiro comando
st.set_page_config(
    page_title="Gráficos",
    page_icon="https://img.freepik.com/vetores-gratis/grafico-de-crescimento-dos-negocios-em-ascensao_1308-170777.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Página inicial: 🌍 https://nucleo.streamlit.app/"}
)

if "expand_file_uploader" not in st.session_state:
    st.session_state["expand_file_uploader"] = True

# Função para verificar e ordenar colunas, incluindo diferentes tipos de dados
def ordenar_coluna(df, coluna, ascending):
    if coluna == "Horas Extras":
        # Tratamento para colunas de tempo (HH:MM)
        df["Horas Extras Minutos"] = df["Horas Extras"].apply(convert_time_to_minutes)
        df = df.sort_values(by="Horas Extras Minutos", ascending=ascending)
        df["Horas Extras"] = df["Horas Extras Minutos"].apply(minutes_to_time)
        df = df.drop(columns=["Horas Extras Minutos"])
    elif pd.api.types.is_numeric_dtype(df[coluna]):
        # Ordenação para colunas numéricas
        df = df.sort_values(by=coluna, ascending=ascending)
    elif pd.api.types.is_datetime64_any_dtype(df[coluna]):
        # Ordenação para colunas de datas
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
        df = df.sort_values(by=coluna, ascending=ascending)
    else:
        # Ordenação para colunas de strings
        df = df.sort_values(by=coluna, ascending=ascending, key=lambda col: col.str.lower())
    return df

config_page()

# Função para converter tempo em formato HH:MM para minutos
# Variável global para controlar mensagens de erro
error_displayed = False

# Função para converter tempo em formato HH:MM para minutos
@st.cache_data
def convert_time_to_minutes(time_str):
    global error_displayed
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except AttributeError:
        if not error_displayed:
            st.error(
                "⚠️ Erro ao processar os dados: Um valor numérico foi encontrado na coluna de tempo. "
                "Certifique-se de que todos os valores na coluna estejam no formato HH:MM."
            )
            error_displayed = True  # Marca o erro como exibido
        return None
    except ValueError:
        if not error_displayed:
            st.error(
                "⚠️ Erro ao processar os dados: Um valor inesperado foi encontrado na coluna de tempo. "
                "Certifique-se de que todos os valores estejam no formato correto (HH:MM)."
            )
            error_displayed = True  # Marca o erro como exibido
        return None

# Função para converter minutos de volta para o formato HH:MM
@st.cache_data
def minutes_to_time(minutes):
    if minutes is None:
        return "00:00"  # Retorna '00:00' para valores None
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02}"

# Função para carregar os dados do arquivo
@st.cache_data
def load_data(uploaded_file, skip_rows=0):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, skiprows=skip_rows)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, skiprows=skip_rows)
    else:
        return None

    # Conversão automática de colunas com valores numéricos para float/int
    for col in df.columns:
        # Tenta converter cada coluna para numérica
        df[col] = pd.to_numeric(df[col], errors='ignore')  # 'ignore' mantém strings como estão

    return df

# Gera o texto formatado para o tooltip dinamicamente e colorido
def generate_hovertemplate(selected_columns):
    hover_text = []
    for i, col in enumerate(selected_columns):
        hover_text.append(
            f"<b style='color:black'>{col}:</b> <span style='color:blue'>%{{customdata[{i}]}}</span><br>"
        )
    return "".join(hover_text) + "<extra></extra>"

# Função para exibir gráficos e data_editor
# Função para gerar ticks para o eixo Y (tempo em minutos ou outros formatos)
def generate_ticks(df, column):
    if column == "Horas Extras Minutos":
        max_val = int(df[column].max())  # Garante que max_val seja inteiro
        tick_step = max(30, max_val // 10)  # Exibir ticks a cada 30 minutos ou 10 divisões
        tick_vals = list(range(0, max_val + tick_step, tick_step))  # Intervalo dos ticks
        tick_texts = [minutes_to_time(val) for val in tick_vals]  # Converter minutos de volta para HH:MM
        return tick_vals, tick_texts
    elif pd.api.types.is_numeric_dtype(df[column]):
        max_val = int(df[column].max())  # Garante que max_val seja inteiro
        tick_step = max(1, max_val // 10)  # Dividir em 10 intervalos
        tick_vals = list(range(0, max_val + tick_step, tick_step))
        return tick_vals, tick_vals  # Para numéricos, os ticks são os próprios valores
    else:
        unique_vals = df[column].unique()
        return unique_vals, unique_vals

# Criação das colunas
col1, col2 = st.sidebar.columns([0.2, 1])

with col1:
    st.subheader("![GIF](https://static.wixstatic.com/media/d8a964_46586e54af604cfe99b47f4c3ad7b2ed~mv2.gif)", divider="rainbow")

with col2:
    st.subheader("📈:green[**DADOS**] Estatísticos", divider="rainbow")
    st.subheader("📉:green[**GRÁFICOS**] Estatísticos", divider="rainbow")

st.logo("https://static.tildacdn.net/tild6338-3232-4634-b733-666338333564/giphy.gif", size="large")

with st.sidebar.expander(":green[**CARREGAR**] ARQUIVO", expanded=st.session_state["expand_file_uploader"], icon=":material/contextual_token_add:"):
    uploaded_file = st.file_uploader("📊 :green[**Carregue um arquivo para criar um gráfico**]", type=["xlsx", "csv"])
    if uploaded_file:
        st.session_state["expand_file_uploader"] = False  # Fecha o expander após upload

# Função para exibir gráfico
def exibir_grafico(uploaded_file):
    try:
        skip_rows = st.sidebar.number_input("Linhas a descartar", min_value=0, value=0, step=1)
        df = load_data(uploaded_file, skip_rows)

        if df is None:
            st.error("Erro ao carregar o arquivo.")
            return

        # Configurações adicionais
        x_axis = st.sidebar.selectbox("Eixo X", df.columns)
        y_axis = st.sidebar.selectbox("Eixo Y", df.columns)

        # Gerar gráfico
        fig = px.bar(df, x=x_axis, y=y_axis)
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    st.write("Nenhum arquivo carregado.")
