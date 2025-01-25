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


# # Função para carregar os dados do arquivo
# @st.cache_data
# def load_data(uploaded_file, skip_rows=0):
#     if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file, skiprows=skip_rows)
#     elif uploaded_file.name.endswith(".xlsx"):
#         df = pd.read_excel(uploaded_file, skiprows=skip_rows)
#     else:
#         return None

#     # Conversão automática de colunas com valores numéricos para float/int
#     for col in df.columns:
#         try:
#             df[col] = pd.to_numeric(df[col])  # Tenta converter a coluna para numérico
#         except ValueError:
#             # Se a conversão falhar, mantém a coluna como está
#             st.warning(f"Não foi possível converter a coluna '{col}' para numérico.")

#     return df

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
       
def exibir_grafico(uploaded_file=None):
    # Inicializa text_col com None
    text_col = None

    if not uploaded_file:
        st.markdown(get_markdown())
        return

    try:
        # Configuração inicial
        with st.sidebar.expander(":blue[**AJUSTAR**] Colunas e Linhas", expanded=False, icon=":material/tune:"):
            skip_rows = st.number_input(":red[**Linhas**] :blue[**a Descartar**]", min_value=0, value=0, step=1, placeholder="Quantas linhas pular", help="Número de linhas a serem ignoradas no início do arquivo")
            df = load_data(uploaded_file, skip_rows)

            if df is None or df.empty:
                st.error("Tipo de arquivo não suportado ou arquivo vazio.")
                return

            # Primeira Coluna
            primary_col = st.selectbox(":green[**Primeira**] :blue[**Coluna**]", options=df.columns, index=0, help=":blue[**Selecione**] a primeira coluna para exibir")
            if primary_col:
                df = df[[primary_col] + [col for col in df.columns if col != primary_col]]

            # Filtro de valores nulos
            filter_col = st.selectbox(":red[**Excluir**] :blue[**Valores Nulos**]", [None] + list(df.columns), help="Selecione a coluna para filtrar valores nulos")
            if filter_col:
                df[filter_col] = df[filter_col].replace("00:00", pd.NA)
                df = df.dropna(subset=[filter_col])
                df = df.reset_index(drop=True)

            # Ordenação do eixo X
            sort_col_x = st.selectbox(":green[**Ordenar**] :blue[**eixo X por**]", options=df.columns, index=0, help="Selecione a coluna para ordenar")
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

        # Exibição de Dados com Data Editor
        with st.expander(":blue[**DADOS**] EDITAR E VISUALIZAR", icon=":material/format_list_bulleted:"):
            df_filtered = st.data_editor(
                df_filtered.reset_index(drop=True),  # Reseta o índice para evitar duplicação
                use_container_width=True,
                num_rows="dynamic"  # Permite o ajuste dinâmico do número de linhas
            )

        # Seleção de colunas para texto nas barras
        with st.sidebar.expander(":blue[**TEXTO NAS BARRAS**] _(opcional)_", expanded=False, icon=":material/format_shapes:"):
            text_cols = st.multiselect(
                ":blue[**Colunas para texto nas barras**]",
                options=df_filtered.columns,
                placeholder="📊 Texto nas barras",
                default=[],  # Nenhuma coluna selecionada por padrão
                help="Selecione as colunas que deseja exibir como texto dentro das barras"
            )

        # Criar o texto para as barras
        if text_cols:
            # Concatenar valores das colunas selecionadas em uma nova coluna "Texto Barras"
            df_filtered["Texto Barras"] = df_filtered[text_cols].apply(
                lambda row: " | ".join(row.values.astype(str)), axis=1
            )
            text_col = "Texto Barras"
        else:
            # Não criar texto nas barras quando nenhuma coluna for selecionada
            df_filtered["Texto Barras"] = ""
            text_col = None

        # Configuração de Gráficos
        # Configuração de Gráficos
        with st.sidebar.expander(":blue[**ESCOLHER**] Eixos e Legendas", expanded=False, icon=":material/checklist:"):
            x_axis = st.selectbox(":blue[**➡️ Eixo X**]", df_filtered.columns)
            y_axis = st.selectbox(":blue[**⬆️ Eixo Y**]", df_filtered.columns)
            # color_col = st.selectbox(":rainbow[**Coluna para cor**] _(opcional)_", [None] + list(df_filtered.columns))


            color_col = st.selectbox(
                ":rainbow[**Coluna para cor**] _(opcional)_",
                ["Selecione"] + list(df_filtered.columns)
            )
            
            # Tratamento caso o usuário não tenha selecionado nenhuma coluna
            if color_col == "Selecione":
                color_col = None  # Define como None para compatibilidade com o restante do código
            



        # # Converter a coluna "Horas Extras" para minutos
        # if "Horas Extras" in df_filtered.columns:
        #     df_filtered["Horas Extras Minutos"] = df_filtered["Horas Extras"].apply(convert_time_to_minutes)
        #     y_axis = "Horas Extras Minutos"  # Usa a nova coluna para lógica do gráfico


        # Converter a coluna "Horas Extras" para minutos apenas se ela for escolhida como eixo Y
        if y_axis == "Horas Extras" and "Horas Extras" in df_filtered.columns:
            df_filtered["Horas Extras Minutos"] = df_filtered["Horas Extras"].apply(convert_time_to_minutes)
            y_axis = "Horas Extras Minutos"  # Usa a nova coluna para lógica do gráfico
        





        # Gerar os ticks para o eixo Y
        tick_vals, tick_texts = generate_ticks(df_filtered, y_axis)

        # Criação do Gráfico Principal
        if x_axis and y_axis:
            labels = {x_axis: x_axis, y_axis: y_axis}
            if color_col:
                labels[color_col] = color_col

            fig = px.bar(
                df_filtered,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text=text_col if "text_col" in locals() else None,
                labels=labels,
                custom_data=[df_filtered[col].fillna('') for col in selected_columns]
            )

            # Configurar o texto para aparecer dentro das barras e ajustar o tooltip
            fig.update_traces(
                texttemplate='<b>%{text}</b>' if "text_col" in locals() else None,
                textposition='inside',
                hovertemplate="<b>%{x}</b><br>" + "<br>".join(
                    [f"{col}: <span style='color:blue;'>%{{customdata[{i}]}}</span>" for i, col in
                     enumerate(selected_columns)])
            )

            # Adicionar título e ticks personalizados ao gráfico
            fig.update_layout(
                title="📊 Estatísticas",
                yaxis=dict(
                    range=[0, None],  # Inicia no zero
                    tickmode="array",
                    tickvals=tick_vals,
                    ticktext=tick_texts,
                    title="Horas Extras"
                )
            )


        # Seleção de colunas para texto nas barras
        with st.sidebar.expander(":blue[**TEXTO NAS BARRAS**] _(opcional)_", expanded=False, icon=":material/format_shapes:"):
            text_cols = st.multiselect(
                ":blue[**Colunas para texto nas barras**]",
                options=df_filtered.columns,
                placeholder="Colunas para exibir como texto nas barras",
                default=[],  # Nenhuma coluna selecionada por padrão
                help="Selecione as colunas que deseja exibir como texto dentro das barras"
            )


        # Criar o texto para as barras
        if text_cols:
            # Concatenar valores das colunas selecionadas em uma nova coluna "Texto Barras"
            df_filtered["Texto Barras"] = df_filtered[text_cols].apply(
                lambda row: " | ".join(row.values.astype(str)), axis=1
            )
            text_col = "Texto Barras"
        else:
            # Caso nenhuma coluna seja selecionada, usar os valores do eixo X como padrão
            df_filtered["Texto Barras"] = df_filtered[x_axis].astype(str)
            text_col = "Texto Barras"

        # Expander para renomear os eixos e título do gráfico
        with st.sidebar.expander(":blue[**RENOMEAR**] Eixos e Título do Gráfico", expanded=False, icon=":material/insert_text:"):
            x_label = st.text_input(":blue[**➡️ Eixo X**]", value=x_axis, help="Insira um rótulo para o eixo X")
            y_label = st.text_input(":blue[**⬆️ Eixo Y**]", value=y_axis, help="Insira um rótulo para o eixo Y")
            legend_title = st.text_input(":blue[**Legenda**]", value=color_col if color_col else "Legenda", help="Insira um título para a legenda")
            title = st.text_input(":blue[**Título do Gráfico**]", value="📊 Estatísticas", help="Insira um título para o gráfico")

        # Configuração de rótulos para o gráfico
        labels = {x_axis: x_label, y_axis: y_label}
        if color_col:
            labels[color_col] = legend_title

        # Criação do Gráfico Principal
        if x_axis and y_axis:
            fig = px.bar(
                df_filtered,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text=text_col if "text_col" in locals() else None,
                labels=labels,
                custom_data=[df_filtered[col].fillna('') for col in selected_columns]
            )

            # Configurar o texto para aparecer dentro das barras e ajustar o tooltip
            fig.update_traces(
                texttemplate='<b>%{text}</b>' if "text_col" in locals() else None,
                textposition='inside',
                hovertemplate="<b>%{x}</b><br>" + "<br>".join(
                    [f"{col}: <span style='color:blue;'>%{{customdata[{i}]}}</span>" for i, col in
                     enumerate(selected_columns)])
            )

            # Adicionar título e ticks personalizados ao gráfico
            fig.update_layout(
                title=title,
                yaxis=dict(
                    range=[0, None],  # Inicia no zero
                    tickmode="array",
                    tickvals=tick_vals,
                    ticktext=tick_texts,
                    title=y_label  # Usa o rótulo personalizado para o eixo Y
                ),
                xaxis=dict(
                    title=x_label  # Usa o rótulo personalizado para o eixo X
                )
            )

            # Renderizar o gráfico
            st.plotly_chart(fig, use_container_width=True, key="main_graph")


    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")






st.logo("https://static.tildacdn.net/tild6338-3232-4634-b733-666338333564/giphy.gif", size="large")

with st.sidebar.expander(":green[**CARREGAR**] ARQUIVO", expanded=st.session_state["expand_file_uploader"], icon=":material/contextual_token_add:"):
    uploaded_file = st.file_uploader("📊 :green[**Carregue um arquivo para criar um gráfico**]", type=["xlsx", "csv"])
    if uploaded_file:
        st.session_state["expand_file_uploader"] = False  # Fecha o expander após upload

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    exibir_grafico()
