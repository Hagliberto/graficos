import pandas as pd
import plotly.express as px
import streamlit as st
from observacao import get_markdown  # Importa o Markdown
from config_page import config_page

# Configuração da página deve ser o primeiro comando
st.set_page_config(
    page_title="Gráficos",
    page_icon="📊",
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

                # Aplicação da ordenação no DataFrame
                if sort_col_x:
                    df = df.sort_values(by=sort_col_x, ascending=sort_ascending_x)
                if sort_col_y:
                    df = df.sort_values(by=sort_col_y, ascending=sort_ascending_y)

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




        # Criação do gráfico
        # Criação e renderização do gráfico
        if x_axis and y_axis:
            # Configura os labels para o gráfico
            labels = {x_axis: x_label, y_axis: y_label}
            if color_col:
                labels[color_col] = legend_title
        
            try:
                # Força a conversão da coluna do eixo X para string
                edited_df[x_axis] = edited_df[x_axis].astype(str)
        
                # Força a conversão da coluna do eixo Y para string (se necessário, como em "Matrícula")
                edited_df[y_axis] = edited_df[y_axis].astype(str)
        
                # Caso o eixo Y contenha minutos (como em "Horas Extras"), converta para HH:MM
                if y_axis == "Horas Extras" or edited_df[y_axis].str.contains(":").any():
                    edited_df[y_axis] = edited_df[y_axis].apply(convert_time_to_minutes).apply(minutes_to_time)
        
                # Caso o eixo X contenha minutos (como em "Horas Extras"), converta para HH:MM
                if x_axis == "Horas Extras" or edited_df[x_axis].str.contains(":").any():
                    edited_df[x_axis] = edited_df[x_axis].apply(convert_time_to_minutes).apply(minutes_to_time)
            except Exception as e:
                st.warning(f"Erro ao ajustar os eixos: {e}")
        
            # Criação do gráfico com rótulos personalizados
            fig = px.bar(
                edited_df,
                x=x_axis,
                y=y_axis,
                color=color_col,
                text=text_col,
                labels=labels  # Aplica os rótulos personalizados
            )
        
            # Configura texto das barras (se texto estiver configurado)
            if text_col:
                fig.update_traces(texttemplate='%{text}', textposition='outside')
        
            # Aplica títulos aos eixos e legenda
            fig.update_layout(
                xaxis_title=x_label,  # Força o título do eixo X
                yaxis_title=y_label,  # Força o título do eixo Y
                legend_title=dict(text=legend_title)  # Força o título da legenda
            )
        
            # Renderiza o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Selecione colunas para os eixos X e Y.")
        
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")



        # Certifique-se de que a coluna selecionada para o eixo Y seja convertida para minutos
        # Conversão do eixo Y para minutos, se necessário
        if y_axis:
            try:
                # Verifica se a coluna é do tipo string contendo ":"
                if edited_df[y_axis].dtype == "object" and edited_df[y_axis].str.contains(":").any():
                    edited_df[y_axis] = edited_df[y_axis].apply(convert_time_to_minutes)
            except Exception as e:
                st.warning(f"Erro ao converter a coluna '{y_axis}' para minutos: {e}")
        
        # # Criação do gráfico
        # if x_axis and y_axis:
        #     # Configura os labels para o gráfico
        #     labels = {x_axis: x_label, y_axis: y_label}
        #     if color_col:
        #         labels[color_col] = legend_title
        
        #     # Criação do gráfico de barras com rótulos personalizados
        #     fig = px.bar(
        #         edited_df,
        #         x=x_axis,
        #         y=y_axis,
        #         color=color_col,
        #         text=text_col,
        #         labels=labels  # Aplica os rótulos personalizados
        #     )
        
        #     # Configura texto das barras (se texto estiver configurado)
        #     if text_col:
        #         fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        #     # Aplica títulos aos eixos e legenda
        #     fig.update_layout(
        #         xaxis_title=x_label,  # Força o título do eixo X
        #         yaxis_title=y_label,  # Força o título do eixo Y
        #         legend_title=dict(text=legend_title)  # Força o título da legenda
        #     )
        
        #     # Renderiza o gráfico no Streamlit
        #     st.plotly_chart(fig, use_container_width=True)
        # else:
        #     st.warning("Selecione colunas para os eixos X e Y.")
        
        
        




# Upload de arquivo
with st.sidebar.expander(":green[**CARREGAR**] ARQUIVO", expanded=True, icon=":material/contextual_token_add:"):
    uploaded_file = st.file_uploader("📊 :green[**Carregue um arquivo para criar um gráfico**]", type=["xlsx", "csv"])

if uploaded_file:
    exibir_grafico(uploaded_file)
else:
    exibir_grafico()
