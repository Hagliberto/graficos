import pandas as pd
import plotly.express as px
import streamlit as st
from observacao import get_markdown
from config_page import config_page

# Configuração inicial da página
st.set_page_config(
    page_title="Gráficos",
    page_icon="https://img.freepik.com/vetores-gratis/grafico-de-crescimento-dos-negocios-em-ascensao_1308-170777.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Página inicial: 🌍 https://nucleo.streamlit.app/"}
)

def ordenar_coluna(df, coluna, ascending):
    if coluna == "Horas Extras":
        df["Horas Extras Minutos"] = df["Horas Extras"].apply(convert_time_to_minutes)
        df = df.sort_values(by="Horas Extras Minutos", ascending=ascending)
        df["Horas Extras"] = df["Horas Extras Minutos"].apply(minutes_to_time)
        df.drop(columns=["Horas Extras Minutos"], inplace=True)
    elif pd.api.types.is_numeric_dtype(df[coluna]):
        df.sort_values(by=coluna, ascending=ascending, inplace=True)
    elif pd.api.types.is_datetime64_any_dtype(df[coluna]):
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
        df.sort_values(by=coluna, ascending=ascending, inplace=True)
    else:
        df.sort_values(by=coluna, ascending=ascending, key=lambda col: col.str.lower(), inplace=True)
    return df

@st.cache_data
def convert_time_to_minutes(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except (AttributeError, ValueError):
        return None

@st.cache_data
def minutes_to_time(minutes):
    if minutes is None:
        return "00:00"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02}"

@st.cache_data
def load_data(uploaded_file, skip_rows=0):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, skiprows=skip_rows)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, skiprows=skip_rows)
        else:
            return None

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception:
                pass
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

def gerar_grafico(df, x_axis, y_axis, color_col, selected_columns, title, x_label, y_label):
    tick_vals, tick_texts = generate_ticks(df, y_axis)
    labels = {x_axis: x_label, y_axis: y_label}
    if color_col:
        labels[color_col] = color_col

    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        color=color_col,
        text=df[selected_columns[0]] if selected_columns else None,
        labels=labels,
        custom_data=[df[col].fillna('') for col in selected_columns]
    )

    fig.update_traces(
        texttemplate='<b>%{text}</b>' if selected_columns else None,
        textposition='inside',
        hovertemplate="<b>%{x}</b><br>" + "<br>".join([
            f"{col}: <span style='color:blue;'>%{{customdata[{i}]}}</span>"
            for i, col in enumerate(selected_columns)])
    )

    fig.update_layout(
        title=title,
        yaxis=dict(
            range=[0, None],
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_texts,
            title=y_label
        ),
        xaxis=dict(title=x_label)
    )

    st.plotly_chart(fig, use_container_width=True)

def generate_ticks(df, column):
    try:
        if column == "Horas Extras Minutos":
            max_val = int(df[column].max())
            tick_step = max(30, max_val // 10)
            tick_vals = list(range(0, max_val + tick_step, tick_step))
            tick_texts = [minutes_to_time(val) for val in tick_vals]
            return tick_vals, tick_texts
        elif pd.api.types.is_numeric_dtype(df[column]):
            max_val = int(df[column].max())
            tick_step = max(1, max_val // 10)
            tick_vals = list(range(0, max_val + tick_step, tick_step))
            return tick_vals, tick_vals
        else:
            unique_vals = df[column].unique()
            return unique_vals, unique_vals
    except Exception as e:
        st.warning(f"Erro ao gerar ticks para o eixo: {e}")
        return [], []

uploaded_file = st.sidebar.file_uploader(
    "📊 Carregue um arquivo para criar um gráfico",
    type=["xlsx", "csv"]
)

if uploaded_file:
    skip_rows = st.sidebar.number_input("Linhas a descartar", min_value=0, value=0, step=1)
    df = load_data(uploaded_file, skip_rows)

    if df is not None:
        x_axis = st.sidebar.selectbox("Eixo X", df.columns)
        y_axis = st.sidebar.selectbox("Eixo Y", df.columns)
        color_col = st.sidebar.selectbox("Coluna para cor (opcional)", [None] + list(df.columns))

        selected_columns = st.sidebar.multiselect(
            "Colunas para exibir", df.columns, default=df.columns
        )

        title = st.sidebar.text_input("Título do Gráfico", "📊 Estatísticas")
        x_label = st.sidebar.text_input("Rótulo do Eixo X", x_axis)
        y_label = st.sidebar.text_input("Rótulo do Eixo Y", y_axis)

        st.subheader(":green[DADOS Estatísticos]")
        with st.expander(":blue[DADOS EDITAR E VISUALIZAR]", expanded=True):
            st.dataframe(df)

        gerar_grafico(df, x_axis, y_axis, color_col, selected_columns, title, x_label, y_label)
    else:
        st.error("Erro: Não foi possível carregar o arquivo.")
