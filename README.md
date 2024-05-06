# Document compare LLM Tool

LLM based tool to compare legal documents. The goal is to generate condensed diff view like the following example:

Artículo 1.

1. España se constituye en un Estado social y democrático de Derecho, que propugna como valores superiores de su ordenamiento jurídico `<del>`la libertad, la justicia, la igualdad y el pluralismo político. `</del>` `<ins>`la unidad, el respeto y el amor.`</ins>`
2. La soberanía nacional reside en el pueblo español, del que emanan los poderes del Estado.
3. `<del>`La forma política del Estado español es la  Monarquía parlamentaria`</del>` `<ins>`La forma política de España es la República parlamentaria.`</ins>`

After that, a explanation for the changes can be generated. The diff view could be conected to an unstructured doc QA app in order to interact with all the changes in a natural way.

# Installation:

Before launching the notebooks it is needed to install the module. Just run the following comand on your terminal:

`pip install git+https://github.com/DivergerThinking/doc_compare_llm`

If you want to run streamlit too, run the following command too:

`pip install "llmdiff[dev] @ git+https://github.com/DivergerThinking/doc_compare_llm"`

The module will be installed in your environment. Make sure you have activated the virtual environment if so. After installing it, you will be able to import the module in python as:

`ìmport llmdiff`

# Usage:

The app can be executed in two modes:

1. Notebooks
2. Streamlit web app

## Notebook mode

The notebook mode consists in three different notebooks. Each one covers a different task and must be executed sequentially. Here are the steps to proceed:

1. Take your OpenAI API key and Organization id, encode it in base64 and place it in a `secrets.json` file under the `data` folder. The json should have this format:

```json
{"openai_api_key": "yourapikey", "organization_id": "yourorgid"}
```

2. Run `clean_text_splitter.ipynb` skipping the cells within the `dev area`.
3. Run `llm_diff.ipynb` skipping the cells within the `dev area`.
4. Play araound and have some fun.

## Streamlit web app mode

1. Open a terminal and move to the repo directory.
2. Run the following command:
   `streamlit run src/llmdiff/streamlit/doc_compare_demo.py`
3. The web interface will open in your default browser.
4. Play around and have some fun.

Note: This demo is slightly hardcoded for the PDFs at `data` folder. 2008 PDF corresponds to original doc and 2018 to modifications doc.
