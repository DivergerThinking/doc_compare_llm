import openai

DIFF_EXPLAINER_PROMPT = """
Eres un experto asistente legal que ayuda a interpretar y entender cambios en legislaciones. Tienes experiencia redactando, corrigiendo y explicando textos legales como leyes o directivas.
Tu objetivo es explicar y resumir los cambios en el texto.
Los cambios se identifican de la siguiente forma:
    - El texto eliminado y/o derogado estará marcado con un tag html <del>.
    - El nuevo texto añadido estará marcado con un tag html <ins>.
La explicación debe ser un resumen conciso y comprensible para personas no acostumbradas a leer documentos legales.
La explicación debe centrarse exclusivamente en los cambios realizados y en las implicaciones de esos cambios.
""" # noqa

EXPLAINER_GEN_PROMPT = """Texto a analizar:
{diff_doc}

Explicación resumida y concisa de los cambios:
"""

def get_diff_explanation(diff_text: str, api_params: dict):
    message_dicts = [
        {"role": "system", "content": DIFF_EXPLAINER_PROMPT},
        {"role": "user", "content": EXPLAINER_GEN_PROMPT.format(diff_doc=diff_text)},
    ]
    response_text = openai.ChatCompletion.create(messages=message_dicts, **api_params).choices[0].message.content
    return response_text