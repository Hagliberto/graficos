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

config_page()

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
# Função para exibir gráficos e data_editor
def exibir_grafico(uploaded_file=None):
    if not uploaded_file:
        st.markdown(get_markdown())
        return

    try:
        # Configurações iniciais para o processamento do arquivo
        with st.sidebar.expander(":blue[**AJUSTAR**] Colunas e Linhas", expanded=False, icon=":material/tune:"):
            skip_rows = st.number_input(":blue[**Linhas a Descartar**]", min_value=0, value=0, step=1, help="Escolha a coluna para excluir", placeholder="Escolha a quantidade de linhas")
            df = load_data(uploaded_file, skip_rows)

            if df is None or df.empty:
                st.error("Tipo de arquivo não suportado ou arquivo vazio.")
                return

            primary_col = st.selectbox(":blue[**Primeira Coluna**]", options=df.columns, index=0, help="A coluna escolhida será a primeira da planilha")

            # Filtro para excluir valores nulos e tratar "00:00"
            filter_col = st.selectbox(":blue[**Excluir Valores Nulos**]", [None] + list(df.columns), help="A coluna escolhida terá as linhas com valores nulos excluídas", placeholder="Escolha uma coluna")
            if filter_col:
                # Substitui valores "00:00" por NaN para filtrar como nulos
                df[filter_col] = df[filter_col].replace("00:00", pd.NA)
                df = df.dropna(subset=[filter_col])

            st.subheader(" ", divider="rainbow")

            # Configuração de ordenação para os eixos
            with st.sidebar.expander(":blue[**ORDENAÇÃO**] Eixos", expanded=False, icon=":material/sort:"):
                # Ordenação do eixo X
                sort_col_x = st.selectbox(":blue[**Ordenar eixo X por**]", options=df.columns, index=0, help="Escolha a coluna para ordenar o eixo X", placeholder="Escolha a coluna")
                sort_ascending_x = st.checkbox(":blue[**Ordem crescente para eixo X**]", value=True, key="sort_x_ascending")

                # Ordenação do eixo Y
                sort_col_y = st.selectbox(":blue[**Ordenar eixo Y por**]", options=df.columns, index=0, help="Escolha a coluna para ordenar o eixo Y", placeholder="Escolha a coluna")
                sort_ascending_y = st.checkbox(":blue[**Ordem crescente para eixo Y**]", value=True, key="sort_y_ascending")

                # Tratamento especial para colunas de tempo durante a ordenação
                if "Horas Extras" in [sort_col_x, sort_col_y]:
                    if sort_col_x == "Horas Extras":
                        df["Horas Extras Minutos"] = df["Horas Extras"].apply(convert_time_to_minutes)
                        df = df.sort_values(by="Horas Extras Minutos", ascending=sort_ascending_x)
                        df["Horas Extras"] = df["Horas Extras Minutos"].apply(minutes_to_time)
                        df = df.drop(columns=["Horas Extras Minutos"])
                    elif sort_col_y == "Horas Extras":
                        df["Horas Extras Minutos"] = df["Horas Extras"].apply(convert_time_to_minutes)
                        df = df.sort_values(by="Horas Extras Minutos", ascending=sort_ascending_y)
                        df["Horas Extras"] = df["Horas Extras Minutos"].apply(minutes_to_time)
                        df = df.drop(columns=["Horas Extras Minutos"])

        df = df[[primary_col] + [col for col in df.columns if col != primary_col]]
        df = df.fillna("Sem Dados")

        # Seleção de colunas para exibição
        with st.sidebar.expander(":blue[**SELECIONAR**] Colunas para Exibir", expanded=False, icon=":material/rule:"):
            selected_columns = st.multiselect("Selecione as colunas a serem exibidas", df.columns, default=df.columns, placeholder="Quais colunas deseja exibir?", help="As colunas escolhidas aparecerão na planilha")
            df = df[selected_columns]

        # Exibição de dados
        with st.expander(":blue[**DADOS**] CARREGADOS", icon=":material/format_list_bulleted:"):
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

        st.subheader("🧮:green[**GRÁFICOS**] Estatísticos", divider="rainbow")

        # Configuração de eixos e legendas
        with st.sidebar.expander(":blue[**ESCOLHER**] Eixos e Legendas", expanded=False, icon=":material/checklist:"):
            x_axis = st.selectbox(":blue[**➡️ Eixo X**]", edited_df.columns)
            y_axis = st.selectbox(":blue[**⬆️ Eixo Y**]", edited_df.columns)
            color_col = st.selectbox(":rainbow[**Coluna para cor**] _(opcional)_", [None] + list(edited_df.columns))
            text_col = st.selectbox(":blue[**Texto nas Barras**] _(opcional)_", [None] + list(edited_df.columns))

        # **Renomeação de eixos e legendas**
        with st.sidebar.expander(":blue[**RENOMEAR**] Eixos e Legendas", expanded=False, icon=":material/format_shapes:"):
            x_label = st.text_input(":blue[**➡️ Eixo X**]", x_axis)
            y_label = st.text_input(":blue[**⬆️ Eixo Y**]", y_axis)
            legend_title = st.text_input(":blue[**Legenda**]", color_col if color_col else "Legenda")

        # Criação do primeiro gráfico
        if x_axis and y_axis:
            # Configuração do gráfico principal
            labels = {x_axis: x_label, y_axis: y_label}
            if color_col:
                labels[color_col] = legend_title

            # Criação do gráfico principal
            fig = px.bar(
                edited_df,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text=text_col,
                labels=labels
            )
            st.plotly_chart(fig, use_container_width=True, key="main_graph")

        # Criação do gráfico TOP dinâmico
        with st.expander("🏆 :green[**GRÁFICO TOP**] Dinâmico", expanded=False, icon=":material/format_list_bulleted:"):
            st.markdown("### :blue[**Escolha o limite para o TOP:**]")
            top_limit = st.slider(":orange[**Quantidade de itens no TOP:**]", min_value=1, max_value=len(df), value=40, step=1)
            coluna_top = st.selectbox(":violet[**Selecione a coluna para o TOP:**]", options=df.columns, index=0)
            ascending_top = st.checkbox(":red[**Ordenar TOP em ordem crescente:**]", value=False)

            # Tratamento especial para "Horas Extras" na coluna TOP
            if coluna_top == "Horas Extras":
                df["Horas Extras Minutos"] = df["Horas Extras"].apply(convert_time_to_minutes)
                top_df = df.sort_values(by="Horas Extras Minutos", ascending=ascending_top).head(top_limit)
                top_df["Horas Extras"] = top_df["Horas Extras Minutos"].apply(minutes_to_time)
                top_df = top_df.drop(columns=["Horas Extras Minutos"])
            else:
                top_df = df.sort_values(by=coluna_top, ascending=ascending_top).head(top_limit)

            # Criação do gráfico TOP
            fig_top = px.bar(
                top_df,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text=text_col,
                labels=labels
            )
            st.plotly_chart(fig_top, use_container_width=True, key="top_graph")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
    


# Upload de arquivo
# st.logo("https://img.freepik.com/vetores-gratis/grafico-de-crescimento-dos-negocios-em-ascensao_1308-170777.jpg")
st.logo("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGI1NXBsY2NoOHE4Z2k0NzIwcmk2eHRhcWQxenllaWU3bzM1dHd6diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/gjrOAylhpZm3dLnO5J/giphy.gif", size="large")
# st.sidebar.image(
#     "https://elbibliote.com/libro-pedia/manual_matematica/wp-content/uploads/2020/07/TH-Financial-business-chart-and-graphs476769843.jpg",
#     width=200  # Ajuste a largura da imagem conforme necessário
# )

with st.sidebar.expander(":green[**CARREGAR**] ARQUIVO", expanded=True, icon=":material/contextual_token_add:"):
    # Adiciona a imagem centralizada usando HTML
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGI1NXBsY2NoOHE4Z2k0NzIwcmk2eHRhcWQxenllaWU3bzM1dHd6diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/gjrOAylhpZm3dLnO5J/giphy.gif" alt="Gráfico" style="width:300px;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Adiciona o carregador de arquivos
    uploaded_file = st.file_uploader("📊 :green[**Carregue um arquivo para criar um gráfico**]", type=["xlsx", "csv"])

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    exibir_grafico()
