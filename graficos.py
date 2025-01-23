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
def generate_hovertemplate(selected_columns):
    hover_text = []
    for i, col in enumerate(selected_columns):
        hover_text.append(
            f"<b style='color:black'>{col}:</b> <span style='color:blue'>%{{customdata[{i}]}}</span><br>"
        )
    return "".join(hover_text) + "<extra></extra>"

# Função para exibir gráficos e data_editor
def exibir_grafico(uploaded_file=None):
    if not uploaded_file:
        st.markdown(get_markdown())
        return

    try:
        # Configuração inicial
        with st.sidebar.expander(":blue[**AJUSTAR**] Colunas e Linhas", expanded=False, icon=":material/tune:"):
            skip_rows = st.number_input(":blue[**Linhas a Descartar**]", min_value=0, value=0, step=1, help="Escolha a coluna para excluir")
            df = load_data(uploaded_file, skip_rows)

            if df is None or df.empty:
                st.error("Tipo de arquivo não suportado ou arquivo vazio.")
                return

            # Primeira Coluna
            primary_col = st.selectbox(":blue[**Primeira Coluna**]", options=df.columns, index=0)
            if primary_col:
                df = df[[primary_col] + [col for col in df.columns if col != primary_col]]

            # Filtro de valores nulos
            filter_col = st.selectbox(":blue[**Excluir Valores Nulos**]", [None] + list(df.columns))
            if filter_col:
                df[filter_col] = df[filter_col].replace("00:00", pd.NA)
                df = df.dropna(subset=[filter_col])
                df = df.reset_index(drop=True)

            # Ordenação do eixo X
            sort_col_x = st.selectbox(":blue[**Ordenar eixo X por**]", options=df.columns, index=0)
            sort_ascending_x = st.checkbox(":blue[**Ordem crescente para eixo X**]", value=True)
            if sort_col_x:
                df = ordenar_coluna(df, sort_col_x, sort_ascending_x)

        # Seleção de Colunas para Exibição
        with st.sidebar.expander(":blue[**SELECIONAR**] Colunas para Exibir", expanded=False, icon=":material/rule:"):
            selected_columns = st.multiselect(
                ":red[**Exibir colunas**]",
                df.columns,
                default=df.columns,
                placeholder="Selecione as colunas para exibir",
                help="Selecione as colunas que deseja exibir no gráfico.",
                key="selected_columns"
            )

        # Filtra o DataFrame com base nas colunas selecionadas
        if selected_columns:
            df_filtered = df[selected_columns]
        else:
            df_filtered = df  # Se nenhuma coluna for selecionada, mostra todas as colunas

        # Configuração de Gráficos
        st.subheader("🧮:green[**GRÁFICOS**] Estatísticos", divider="rainbow")
        with st.sidebar.expander(":blue[**ESCOLHER**] Eixos e Legendas", expanded=False, icon=":material/checklist:"):
            x_axis = st.selectbox(":blue[**➡️ Eixo X**]", df_filtered.columns)
            y_axis = st.selectbox(":blue[**⬆️ Eixo Y**]", df_filtered.columns)
            color_col = st.selectbox(":rainbow[**Coluna para cor**] _(opcional)_", [None] + list(df_filtered.columns))

            # Novo multiselect para texto nas barras
            text_cols = st.multiselect(
                ":blue[**Texto nas Barras**] _(opcional)_",
                options=df_filtered.columns,
                default=None,
                help="Selecione uma ou mais colunas para exibir como texto nas barras"
            )

        # Personalizar o texto exibido dentro das barras
        if text_cols:
            def format_text(row):
                # Formatar o texto com o nome da coluna em preto e o valor em outra cor
                formatted_text = "<br>".join([
                    f"<b style='color:black'>{col}:</b> <span style='color:blue'>{row[col]}</span>"
                    for col in text_cols
                ])
                return formatted_text

            # Adicionar coluna de texto formatado ao DataFrame
            df_filtered["Texto Barras"] = df_filtered.apply(format_text, axis=1)
            text_col = "Texto Barras"
        else:
            # Caso nenhuma coluna seja selecionada, usar os valores dos eixos X e Y
            df_filtered["Texto Barras"] = df_filtered.apply(lambda row: f"{row[x_axis]}: {row[y_axis]}", axis=1)
            text_col = "Texto Barras"

        with st.sidebar.expander(":blue[**RENOMEAR**] Eixos e Legendas", expanded=False, icon=":material/format_shapes:"):
            x_label = st.text_input(":blue[**➡️ Eixo X**]", value=x_axis, help="Insira um rótulo para o eixo X")
            y_label = st.text_input(":blue[**⬆️ Eixo Y**]", value=y_axis, help="Insira um rótulo para o eixo Y")
            legend_title = st.text_input(":blue[**Legenda**]", value=color_col if color_col else "Legenda", help="Insira um título para a legenda")
            title = st.text_input(":blue[**Título do Gráfico**]", value="📊 Estatísticas", help="Insira um título para o gráfico")

        # Exibição de Dados
        with st.expander(":blue[**DADOS**] CARREGADOS", icon=":material/format_list_bulleted:"):
            edited_df = st.data_editor(df_filtered.reset_index(drop=True), use_container_width=True, num_rows="dynamic")

        # Atualizar o DataFrame com as edições
        df_filtered = edited_df

        # Criação do Gráfico Principal
        if x_axis and y_axis:
            labels = {x_axis: x_label, y_axis: y_label}
            if color_col:
                labels[color_col] = legend_title

            try:
                # Lógica para criar gráfico
                fig = px.bar(
                    df_filtered,
                    x=x_axis,
                    y=y_axis,
                    color=color_col,
                    text=text_col,  # Usa o texto formatado ou os valores dos eixos X e Y
                    labels=labels,
                    custom_data=[df_filtered[col].fillna('') for col in selected_columns]  # Passa as colunas selecionadas para o customdata, preenchendo valores ausentes com uma string vazia
                )

                # Configurar o texto para aparecer dentro das barras e ajustar o tooltip
                fig.update_traces(
                    texttemplate='<b>%{text}</b>',  # Mostra o texto formatado dentro das barras
                    textposition='inside',  # Texto dentro das barras
                    insidetextanchor='middle',  # Centraliza verticalmente
                    textfont=dict(size=12),  # Define o tamanho da fonte
                    hovertemplate="<b>%{x}</b><br>" + "<br>".join([f"{col}: <span style='color:blue;'>%{{customdata[{i}]}}</span>" for i, col in enumerate(selected_columns)])  # Configura o tooltip dinamicamente e colorido
                )

                # Adicionar título ao gráfico
                fig.update_layout(title=title)

                # Renderizar o gráfico
                st.plotly_chart(fig, use_container_width=True, key="main_graph")

            except KeyError as e:
                st.error(f"Erro ao criar o gráfico: A coluna {e} não foi encontrada no dataframe. Verifique as colunas selecionadas.")
            except ValueError as e:
                st.error(f"Erro de valor: {str(e)}. Verifique os dados e tente novamente.")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}. Tente novamente ou contate o suporte.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.logo("https://static.tildacdn.net/tild6338-3232-4634-b733-666338333564/giphy.gif", size="large")

with st.sidebar.expander(":green[**CARREGAR**] ARQUIVO", expanded=True, icon=":material/contextual_token_add:"):
    # Adiciona o carregador de arquivos
    uploaded_file = st.file_uploader("📊 :green[**Carregue um arquivo para criar um gráfico**]", type=["xlsx", "csv"])

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    exibir_grafico()
