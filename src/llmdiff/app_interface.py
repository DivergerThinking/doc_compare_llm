import tempfile
import os
import openai
import re
import fitz
import streamlit as st
from text_splitter import clean_source_text, split_by_article, split_by_parentheses_enum_list
from differ import auto_generate_diff_text
from diff_explainer import get_diff_explanation


OPENAI_MODEL_MAP = {":rainbow[GPT-4]": "gpt-4", "***GPT-3.5***": "gpt-3.5-turbo-16k"}
HTML_BOX_TEMPLATE = """<p style="padding: 0 10px 0 10px; background-color: rgb(240, 242, 246); border-radius: 10px";>
        {text}</p>"""


def read_pdf(file_path):
    with fitz.open(file_path) as doc:
        whole_text = ""
        for page in doc:
            text = page.get_text()
            whole_text = whole_text + "\n\n" + text
    return whole_text


def string_to_markdown(text):
    text = re.sub("```", "", text)
    text = re.sub("\n", "<br>", text)
    return text


def change_mod_text_state():
    st.session_state.modified_text = ""


def llm_diff(selected_mod):
    diff_api_params = {
        "model": st.session_state.openai_model,
        "request_timeout": None,
        "max_tokens": 2000,
        "stream": False,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "api_base": "",
        "organization": st.session_state.openai_org_id,
    }
    id_article_api_params = {
        "model": "gpt-3.5-turbo-16k",
        "request_timeout": None,
        "max_tokens": 2000,
        "stream": False,
        "n": 1,
        "temperature": 0,
        "top_p": 1,
        "api_base": "",
        "organization": st.session_state.openai_org_id,
    }
    response = auto_generate_diff_text(
        origin_docs=st.session_state.articles,
        mod_docs={0: st.session_state.modifications[selected_mod]},
        diff_api_params=diff_api_params,
        id_article_api_params=id_article_api_params,
    )
    modified_text = "Los artículos quedan modificados como sigue:"
    for _, v in response.items():
        if not v:
            continue
        temp_text = string_to_markdown(v)
        modified_text += f"<br><br>{temp_text}<br>"
    return modified_text


def process_pdfs(origin_source, mods_source):
    # Verificar si input_source es un objeto UploadedFile
    if hasattr(origin_source, "read"):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(origin_source.getvalue())
            temp_path = temp_file.name
        text = read_pdf(temp_path)
        os.remove(temp_path)
    else:
        text = read_pdf(origin_source)
    clean_text = clean_source_text(text)
    articles = split_by_article(clean_text)
    st.session_state.articles = articles

    # Verificar si input_source es un objeto UploadedFile
    if hasattr(mods_source, "read"):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(mods_source.getvalue())
            temp_path = temp_file.name
        text = read_pdf(temp_path)
        os.remove(temp_path)
    else:
        text = read_pdf(mods_source)
    clean_text = clean_source_text(text)
    articles = split_by_article(clean_text)
    modifications = split_by_parentheses_enum_list(articles["articulo_1"])
    st.session_state.modifications = modifications


def app():
    if not hasattr(st.session_state, "articles"):
        st.session_state.articles = {}
    if not hasattr(st.session_state, "modifications"):
        st.session_state.modifications = {}
    if not hasattr(st.session_state, "disable_app"):
        st.session_state.disable_app = True
    if not hasattr(st.session_state, "sbox_viz"):
        st.session_state.sbox_viz = False
    if not hasattr(st.session_state, "modified_text"):
        st.session_state.modified_text = ""

    st.title("Comparador de documentos")

    st.sidebar.title("Configuración")
    openai.api_key = st.sidebar.text_input("Ingrese su openai api key:")
    st.session_state.openai_org_id = st.sidebar.text_input("Ingrese su openai organization id:")
    radio_model = st.sidebar.radio(
        "Elige qué modelo de OpenAI usar:",
        [":rainbow[GPT-4]", "***GPT-3.5***"],
        captions=[
            "Modelo más potente y caro, que ejecuta la tarea precisa y correctamente.",
            "Modelo equivalente a ChatGPT. No garantiza una ejecución correcta de la tarea.",
        ],
    )
    st.session_state.openai_model = OPENAI_MODEL_MAP[radio_model]

    with st.expander("Mostrar carga de documentos:", True):
        col1, col2 = st.columns(2)
        with col1:
            origin_pdf_source = st.file_uploader(
                "Cargue el PDF de la legislación original:", type=["pdf"], key="origin_pdf"
            )
        with col2:
            mods_pdf_source = st.file_uploader(
                "Cargue el PDF de modificaciones de la legislación:", type=["pdf"], key="mods_pdf"
            )

        if st.button("Procesar documentos de entrada"):
            process_pdfs(origin_pdf_source, mods_pdf_source)
            st.session_state.disable_app = False
            st.session_state.sbox_viz = True

    if st.session_state.sbox_viz:
        selected_mod = st.selectbox(
            "Selecciona la modificación",
            st.session_state.modifications.keys(),
            disabled=st.session_state.disable_app,
            on_change=change_mod_text_state
        )
        selected_mod_text = st.session_state.modifications[selected_mod]
        selected_mod_text = string_to_markdown(selected_mod_text)
        selected_mod_md = HTML_BOX_TEMPLATE.format(text=selected_mod_text)
        st.markdown(selected_mod_md, unsafe_allow_html=True)
        # st.session_state.modified_text = ""

    if st.button("Generar documento modificado", disabled=st.session_state.disable_app):
        st.session_state.modified_text = llm_diff(selected_mod)

    if st.session_state.modified_text:
        mod_md_html = HTML_BOX_TEMPLATE.format(text=st.session_state.modified_text)
        st.markdown(mod_md_html, unsafe_allow_html=True)

    if st.session_state.modified_text:
        if st.button("Generar explicación de las modificaciones"):
            explanation = get_diff_explanation(
                st.session_state.modified_text,
                {
                    "model": st.session_state.openai_model,
                    "organization": st.session_state.openai_org_id,
                },
            )
            explanation_md_html = HTML_BOX_TEMPLATE.format(text=string_to_markdown(explanation))
            st.markdown(explanation_md_html, unsafe_allow_html=True)

    # if st.button("reset_sbox"):
    #     st.session_state.sbox_dis = True
    #     st.session_state.sbox_viz = False
    #     st.rerun()

    # if st.button("Limpiar Historial"):
    #     st.session_state.questions_log = []
    #     st.session_state.answers_log = {}
    #     st.sidebar.empty()


if __name__ == "__main__":
    app()
