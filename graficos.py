import pandas as pd
import plotly.express as px
import streamlit as st
from observacao import get_markdown  # Importa o Markdown
from config_page import config_page

# Configuração da página deve ser o primeiro comando
st.set_page_config(
    page_title="Gráficos",
    page_icon="https://img.freepik.com/vetores-gratis/grafico-de-crescimento-dos-negocios-em-ascensao_1308-170777.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Página inicial: 🌍 https://nucleo.streamlit.app/"}
)

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
        return pd.read_csv(uploaded_file, skiprows=skip_rows)
    elif uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file, skiprows=skip_rows)
    else:
        return None

# Gera o texto formatado para o tooltip dinamicamente e colorido
def generate_hovertemplate(df, selected_columns):
    hover_text = []
    for i, col in enumerate(selected_columns):
        hover_text.append(
            f"<b style='color:black'>{col}:</b> <span style='color:blue'>%{{customdata[{i}]}}</span><br>"
        )
    return "".join(hover_text) + "<extra></extra>"


def process_multiple_files(uploaded_files):
    dataframes = {}
    for idx, uploaded_file in enumerate(uploaded_files):
        with st.sidebar.expander(f":blue[**AJUSTAR ARQUIVO {idx+1}**]", expanded=False):
            skip_rows = st.number_input(f":blue[**Linhas a Descartar** - Arquivo {idx+1}]", min_value=0, value=0, step=1)
            df = load_data(uploaded_file, skip_rows)

            if df is None or df.empty:
                st.warning(f"⚠️ Arquivo {uploaded_file.name} está vazio ou não é suportado.")
                continue

            primary_col = st.selectbox(f":blue[**Primeira Coluna - Arquivo {idx+1}**]", options=df.columns, index=0)
            if primary_col:
                df = df[[primary_col] + [col for col in df.columns if col != primary_col]]

            filter_col = st.selectbox(f":blue[**Excluir Valores Nulos - Arquivo {idx+1}**]", [None] + list(df.columns))
            if filter_col:
                df[filter_col] = df[filter_col].replace("00:00", pd.NA)
                df = df.dropna(subset=[filter_col]).reset_index(drop=True)

            sort_col_x = st.selectbox(f":blue[**Ordenar eixo X por - Arquivo {idx+1}**]", options=df.columns, index=0)
            sort_ascending_x = st.checkbox(f":blue[**Ordem crescente - Arquivo {idx+1}**]", value=True)
            if sort_col_x:
                df = ordenar_coluna(df, sort_col_x, sort_ascending_x)

            dataframes[uploaded_file.name] = df

    return dataframes

# Função para exibir gráficos e data_editor
def exibir_grafico(dataframes):
    if not dataframes:
        st.markdown(get_markdown())
        return

    # Unindo os DataFrames com base em uma coluna em comum
    common_col = st.sidebar.selectbox(
        ":blue[**Coluna Comum para União**]", options=list(dataframes.values())[0].columns
    )

    combined_df = pd.concat(dataframes.values(), axis=0, join='outer', ignore_index=True)

    # Seleção de Colunas para Exibição
    with st.sidebar.expander(":blue[**SELECIONAR**] Colunas para Exibir", expanded=False):
        selected_columns = st.multiselect(
            ":red[**Exibir colunas**]",
            combined_df.columns,
            default=combined_df.columns,
            placeholder="Selecione as colunas para exibir",
            help="Selecione as colunas que deseja exibir no gráfico."
        )

    # Filtra o DataFrame com base nas colunas selecionadas
    if selected_columns:
        combined_df = combined_df[selected_columns]

    st.subheader("🧮:green[**GRÁFICOS**] Estatísticos", divider="rainbow")

    # Configuração de Gráficos
    with st.sidebar.expander(":blue[**ESCOLHER**] Eixos e Legendas", expanded=False):
        x_axis = st.selectbox(":blue[**➡️ Eixo X**]", combined_df.columns)
        y_axis = st.selectbox(":blue[**⬆️ Eixo Y**]", combined_df.columns)
        color_col = st.selectbox(":rainbow[**Coluna para cor**] _(opcional)_", [None] + list(combined_df.columns))

        text_cols = st.sidebar.multiselect(
            ":blue[**Texto nas Barras**] _(opcional)_",
            options=combined_df.columns,
            default=None,
            help="Selecione uma ou mais colunas para exibir como texto nas barras"
        )

    if x_axis and y_axis:
        try:
            combined_df["Texto Barras"] = combined_df.apply(
                lambda row: "<br>".join(
                    [f"<b style='color:black'>{col}:</b> <span style='color:blue'>{row[col]}</span>" for col in text_cols]
                ), axis=1
            )

            fig = px.bar(
                combined_df,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text="Texto Barras",
                custom_data=combined_df[selected_columns]
            )

            fig.update_traces(
                texttemplate='%{text}',
                textposition='inside',
                hovertemplate=generate_hovertemplate(combined_df, selected_columns)
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao criar gráfico: {e}")

uploaded_files = st.sidebar.file_uploader(
    ":green[**Carregar Arquivos**]", type=["xlsx", "csv"], accept_multiple_files=True
)

if uploaded_files:
    dataframes = process_multiple_files(uploaded_files)
    exibir_grafico(dataframes)
else:
    st.markdown(get_markdown())
