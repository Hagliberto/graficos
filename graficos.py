import pandas as pd
import plotly.express as px
import streamlit as st
from observacao import get_markdown  # Importa o Markdown

# Configuração da página deve ser o primeiro comando
st.set_page_config(
    page_title="Gráficos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Página inicial: 🌍 https://nucleo.streamlit.app/"}
)

# Função para converter tempo em formato HH:MM para minutos
@st.cache_data
def convert_time_to_minutes(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except ValueError:
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

# Função para exibir gráficos e data_editor
def exibir_grafico(uploaded_file=None):
    if not uploaded_file:
        st.markdown(get_markdown())
        return

    try:
        # Configurações iniciais para o processamento do arquivo
        with st.sidebar.expander(":blue[**AJUSTAR**] Colunas e Linhas", expanded=True):
            skip_rows = st.number_input(":orange[**Linhas a Descartar**]", min_value=0, value=0, step=1, help="Escolha a coluna para excluir", placeholder="Escolha a quantidade de linhas")

            df = load_data(uploaded_file, skip_rows)

            if df is None or df.empty:
                st.error("Tipo de arquivo não suportado ou arquivo vazio.")
                return

            primary_col = st.selectbox(":orange[**Primeira Coluna**]", options=df.columns, index=0, help="A coluna escolhida será a primeira da planilha")

            # Filtro para excluir valores nulos e tratar "00:00"
            filter_col = st.selectbox(":orange[**Excluir Valores Nulos**]", [None] + list(df.columns), help="A coluna escolhida terá as linhas com valores nulos excluídas", placeholder="Escolha uma coluna")
            if filter_col:
                # Substitui valores "00:00" por NaN para filtrar como nulos
                df[filter_col] = df[filter_col].replace("00:00", pd.NA)
                df = df.dropna(subset=[filter_col])
    
            # Ordenação e outras opções
            sort_col = st.selectbox(":orange[**Ordenar por**]", options=df.columns, index=0, help="Escolha a coluna para ordenar", placeholder="Escolha a coluna")
            sort_ascending = st.checkbox(":orange[**Ordem Crescente**]", value=True)
    
            if st.checkbox(":orange[**Coluna é do tipo Tempo (HH:MM)**]", key="sort_col_time"):
                if df[sort_col].apply(lambda x: isinstance(x, str) and ":" in x).all():
                    # Convertendo a coluna de tempo em minutos
                    df[sort_col] = df[sort_col].apply(convert_time_to_minutes)
                    df[f"{sort_col}_formatado"] = df[sort_col].apply(minutes_to_time)  # Coluna formatada de volta para HH:MM
                else:
                    st.warning("A coluna selecionada contém valores inválidos ou no formato errado. Certifique-se de que todos os valores estão no formato HH:MM.")

        # Ordenar com base na coluna de tempo convertida
        df = df.sort_values(by=sort_col, ascending=sort_ascending)

        # Coloque a coluna formatada de volta no DataFrame
        if f"{sort_col}_formatado" in df.columns:
            df[sort_col] = df[f"{sort_col}_formatado"]  # Use a coluna formatada para exibição

        df = df[[primary_col] + [col for col in df.columns if col != primary_col]]

        # Substitui valores nulos (None) por "Sem Dados"
        df = df.fillna("Sem Dados")

        # Seleção de colunas para exibição
        with st.sidebar.expander(":blue[**SELECIONAR**] Colunas para Exibir"):
            selected_columns = st.multiselect("Selecione as colunas a serem exibidas", df.columns, default=df.columns, placeholder="Quais colunas deseja exibir?", help="As colunas escolhidas aparecerão na planilha")
            df = df[selected_columns]

        # Exibição de dados
        with st.expander("📄 Dados Carregados"):
            # Mostra o DataFrame com os valores nulos excluídos
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

        # Configuração de eixos e legendas
        with st.sidebar.expander(":blue[**ESCOLHER**] Eixos e Legendas"):
            x_axis = st.selectbox(":blue[**➡️ Eixo X**]", edited_df.columns)
            y_axis = st.selectbox(":blue[**⬆️ Eixo Y**]", edited_df.columns)
            color_col = st.selectbox(":rainbow[**Coluna para cor**] _(opcional)_", [None] + list(edited_df.columns))
            text_col = st.selectbox(":blue[**Texto nas Barras**] _(opcional)_", [None] + list(edited_df.columns))

        # Renomeação de eixos e legendas
        with st.sidebar.expander(":blue[**RENOMEAR**] Eixos e Legendas"):
            x_label = st.text_input(":blue[**➡️ Eixo X**]", x_axis)
            y_label = st.text_input(":blue[**⬆️ Eixo Y**]", y_axis)
            legend_title = st.text_input(":blue[**Legenda**]", color_col if color_col else "Legenda")

        # Escolha do tipo de gráfico
        with st.sidebar.expander(":blue[**TIPOS DE GRÁFICOS**]"):
            chart_type = st.radio("Tipo de Gráfico", ("📊 Barras", "📈 Linhas"), label_visibility="collapsed")

        # Criação do gráfico
        if x_axis and y_axis:
            if chart_type == "📊 Barras":
                fig = px.bar(
                    edited_df,
                    x=x_axis,
                    y=y_axis,
                    color=color_col,
                    text=text_col,
                    title="📊 Estatística",
                    labels={x_axis: x_label, y_axis: y_label, color_col: legend_title}
                )
            else:
                fig = px.line(
                    edited_df,
                    x=x_axis,
                    y=y_axis,
                    color=color_col,
                    title="📈 Estatística",
                    labels={x_axis: x_label, y_axis: y_label, color_col: legend_title}
                )

            if chart_type == "📊 Barras" and text_col:
                fig.update_traces(texttemplate='%{text}', textposition='outside')

            fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Selecione colunas para os eixos X e Y.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")


# Upload de arquivo
with st.sidebar.expander(":blue[**Upload de Arquivo**]", expanded=True):
    uploaded_file = st.file_uploader(
        ":green[**Faça upload de um arquivo para exibir o gráfico**]",
        type=["xlsx", "csv"]
    )

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    exibir_grafico()
