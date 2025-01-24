# observacao.py
import streamlit as st



def get_markdown():
    
    col1, col2, col3 = st.columns([0.15,1,1])
    
    with col1:
        st.image(
            "https://static.wixstatic.com/media/d8a964_46586e54af604cfe99b47f4c3ad7b2ed~mv2.gif",
            width=100  # Ajuste a largura da imagem conforme necessário
        )


    with col2:    
        st.success("## Sistema de Criação de Gráficos", icon=":material/analytics:")
        st.subheader(" ", divider="rainbow")
        return """
    
    ### 🗂️ **1. Upload de Arquivo**
    - Faça o upload de um arquivo nos formatos **CSV** ou **XLSX** utilizando o botão na barra lateral.
    - O sistema suporta arquivos com colunas contendo dados textuais, numéricos, valores monetários e **datas/horas**.
    - Após carregar o arquivo, você poderá configurar, visualizar e editar os dados para gerar gráficos personalizados.
    
    ---
    
    ### ⚙️ **2. Configurações de Dados**
    #### 📝 **Descartar Linhas Iniciais**
    - Ignore as linhas iniciais do arquivo carregado, caso sejam cabeçalhos ou informações irrelevantes.
    - Insira o número de linhas a descartar no campo disponível.
    
    #### 🔄 **Ordenar Dados**
    - Escolha uma coluna para ordenar os dados.
    - Defina a ordem como **crescente** ou **decrescente** com apenas um clique.
    
    #### 🏷️ **Selecionar Primeira Coluna**
    - Reorganize a tabela exibindo a coluna escolhida como a primeira.
    - As demais colunas serão ordenadas automaticamente após a escolhida.
    
    ---
    
    ### ⏰ **3. Tratamento de Datas e Horas**
    - O sistema detecta automaticamente colunas com valores no formato de **datas** ou **datas e horas**.
    - Colunas reconhecidas como datas podem ser utilizadas para:
      - **Ordenação automática**: Organize as linhas com base em datas cronológicas.
      - **Configuração de eixos**: Selecione colunas de datas para serem utilizadas no eixo **X** ou **Y** dos gráficos.
      - **Filtros temporais**: Selecione intervalos de datas específicos para análise detalhada (dependendo das configurações avançadas).
    - As datas e horas são interpretadas corretamente, mesmo em formatos regionais como `dd/mm/yyyy` ou `mm/dd/yyyy`.
    
    ---
    
    ### 🔍 **4. Seleção de Colunas**
    - Utilize o **multiselect** para selecionar apenas as colunas que deseja visualizar ou incluir no gráfico.
    - Essa funcionalidade é útil para trabalhar apenas com os dados mais relevantes.
    
    ---
    
    ### ✏️ **5. Edição de Dados**
    - Visualize e edite os dados diretamente na seção **📄 Dados Carregados**.
    - Faça ajustes rápidos, como corrigir valores ou atualizar informações, sem necessidade de editar o arquivo original.
    - As alterações realizadas são automaticamente sincronizadas com os gráficos gerados.
    
    ---
    
    ### 📊 **6. Configuração de Gráficos**
    #### 📐 **Eixos do Gráfico**
    - Selecione qual coluna será utilizada como:
      - **Eixo X** (horizontal).
      - **Eixo Y** (vertical).
    - Colunas de **datas** e **horas** são exibidas como opções válidas para criar gráficos temporais.
    
    #### 🎨 **Definir Cores no Gráfico**
    - Opcionalmente, escolha uma coluna para atribuir cores às categorias no gráfico.
    - **Até 3 categorias**: Usará as cores **azul**, **vermelho** e **verde**.
    - **Mais de 3 categorias**: O sistema aplica automaticamente um conjunto de cores adicionais.
    
    ---
    
    ### ✨ **7. Personalização**
    #### 🖋️ **Renomear Eixos e Legenda**
    - Edite os títulos dos eixos **X** e **Y** para adequá-los ao contexto dos dados apresentados.
    - Renomeie a legenda para melhor descrever as categorias exibidas no gráfico.
    
    #### 📊 **Tipos de Gráficos**
    - Escolha entre:
      - **📊 Gráfico de Barras**: Ideal para comparações entre categorias.
      - **📈 Gráfico de Linhas**: Perfeito para dados sequenciais e tendências temporais.
    
    ---
    
    ### 🚀 **8. Visualização do Gráfico**
    - Após configurar os dados e personalizar os gráficos:
      - Visualize gráficos interativos adaptados ao tamanho da tela.
      - Use os gráficos para análise, apresentações ou relatórios.
    
    ---
    
    ### 🛠️ **9. Funcionalidades Avançadas**
    #### 💵 **Processamento Automático de Valores Monetários**
    - O sistema identifica colunas com valores no formato monetário (ex.: `R$ 1.000,00`) e as converte automaticamente para números.
    - Isso permite que os valores sejam utilizados em cálculos e gráficos.
    
    #### ⏳ **Interpretação de Datas/Horas**
    - O sistema interpreta colunas de datas e horas em diversos formatos.
    - Permite que você explore informações temporais com precisão e facilite a análise cronológica dos dados.
    
    #### 🔄 **Sincronização Automática**
    - Todas as edições feitas nos dados são refletidas instantaneamente nos gráficos.
    - Trabalhe com dados atualizados sem a necessidade de recarregar a página.
    
    ---
    
    ### 🎉 **10. Benefícios**
    - Interface intuitiva e interativa.
    - Total compatibilidade com arquivos **CSV**, **XLSX** e colunas de **datas/horas**.
    - Flexibilidade para organizar, editar e personalizar gráficos.
    - Resultados em tempo real.
    
    """
