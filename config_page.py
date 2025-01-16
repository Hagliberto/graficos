import streamlit as st

def config_page():
    footer_style = """
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: var(--background-color);
            color: var(--text-color);
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }
        .footer:hover {
            background-color: #00FF7F;
        }
        
    </style>
    """
    st.markdown(footer_style, unsafe_allow_html=True)

    footer_content = '<div class="footer">👨🏻‍💻 Hagliberto Alves de Oliveira®️</div>'
    st.markdown(footer_content, unsafe_allow_html=True)
