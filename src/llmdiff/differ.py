from openai import OpenAI
import logging

DETECT_ARTICLE_MODIF_SYSTEM_PROMPT = """
Eres un asistente que identifica en un texto legal los artículos que modifica de otra legislación anterior.
La respuesta debe ser únicamente los nombre de los artículos identificados en minúscula, sin tildes y con barra baja en lugar de espacio.
Los artículos identificados deben estar estar formateados como una lista de python ["articulo_1", "articulo_2"].

Ejemplo 1
Texto de modificaciones(encapsulado en triple tilde inversa):
```
El artículo 1 se sustituye por el texto siguiente:
Exposición de motivos y causas.
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
```
Artículos identificados:
["articulo_1"]

Ejemplo 2
Texto de modificaciones(encapsulado en triple tilde inversa):
```
En el artículo 2, apartado 2, se añade la letra siguiente:
Etiam mattis mauris nec felis tempus dapibus.

3) El artículo 3 se modifica como sigue:
Proin pretium, est sed pellentesque rutrum, ipsum felis posuere dui, quis pulvinar nibh neque quis libero.
```
Artículos identificados:
["articulo_1", "articulo_3"]
"""  # noqa: E501


modif_doc_prompt_prompt = """

Texto de modificaciones (encapsulado en triple tilde inversa):
```
{mod_doc}
```

Artículos identificados:
"""


DIFF_SYSTEM_PROMPT = """
Eres un experto asistente legal que ayuda a interpretar y entender cambios en legislaciones. Tienes experiencia redactando, corrigiendo y mejorando textos legales como leyes o directivas.
Tu objetivo es consolidar los cambios en los documentos tachando (usa el tag html <del>) la parte del texto que queda modificada o derogada y añadiendo el nuevo texto  (usa el tag html <ins>). Pueden haber solo eliminaciones o solo adiciones de texto.
El resultado final será un texto único dónde quede claro cuales son las partes del texto que quedan obsoletas y aquellas que entran en vigor.
Deber realizar el trabajo artículo a artículo para evitar errores.
Si las instrucciones de modificación no afectan a los artículos en el documento original, o se trata de otro elemento que no sea un artículo, simplemente responde con un string vacío.

Ejemplo:

Documento original (encapsulado en triple tilde inversa):
```
Constitución española
Artículo 1.
1. España se constituye en un Estado social y democrático de Derecho, que propugna como valores superiores de su ordenamiento jurídico la libertad, la justicia, la igualdad y el pluralismo político.
2. La soberanía nacional reside en el pueblo español, del que emanan los poderes del Estado.
3. La forma política del Estado español es la Monarquía parlamentaria.

Artículo 2.
La Constitución se fundamenta en la indisoluble unidad de la Nación española, patria común e indivisible de todos los españoles, y reconoce y garantiza el derecho a la autonomía de las nacionalidades y regiones que la integran y la solidaridad entre todas ellas.

Artículo 3.
1. El castellano es la lengua española oficial del Estado. Todos los españoles tienen el deber de conocerla y el derecho a usarla.
2. Las demás lenguas españolas serán también oficiales en las respectivas Comunidades Autónomas de acuerdo con sus Estatutos.
3. La riqueza de las distintas modalidades lingüísticas de España es un patrimonio cultural que será objeto de especial respeto y protección.
```

Instrucciones de modificaciones (encapsulado en triple tilde inversa):
```
Constitución Española
Del artículo 1 se modifican los siguientes apartados:
Apartado 1. Se sustituye el texto "la libertad, la justicia, la igualdad y el pluralismo político." por "la unidad, el respeto y el amor."
Apartado 3. Se sustituye por completo por el siguiente texto "La forma política de España es la República parlamentaria."

En el artículo 2 se añade el siguiente texto "Sin menoscabo de su derecho a decidir sobre su futuro.".

En el articulo 3 se elimina el apartado 3.
```

Documento consolidado (encapsulado en triple tilde inversa):
```
Artículo 1.
1. España se constituye en un Estado social y democrático de Derecho, que propugna como valores superiores de su ordenamiento jurídico <del>la libertad, la justicia, la igualdad y el pluralismo político. </del> <ins>la unidad, el respeto y el amor.</ins>
2. La soberanía nacional reside en el pueblo español, del que emanan los poderes del Estado.
3. <del>La forma política del Estado español es la  Monarquía parlamentaria</del> <ins>La forma política de España es la República parlamentaria.</ins>

Artículo 2.
La Constitución se fundamenta en la indisoluble unidad de la Nación española, patria común e indivisible de todos los españoles, y reconoce y garantiza el derecho a la autonomía de las nacionalidades y regiones que la integran y la solidaridad entre todas ellas. <ins>Sin menoscabo de su derecho a decidir sobre su futuro.</ins>

Artículo 3.
1. El castellano es la lengua española oficial del Estado. Todos los españoles tienen el deber de conocerla y el derecho a usarla.
2. Las demás lenguas españolas serán también oficiales en las respectivas Comunidades Autónomas de acuerdo con sus Estatutos.
<del>3. La riqueza de las distintas modalidades lingüísticas de España es un patrimonio cultural que será objeto de especial respeto y protección.</del>
```
"""  # noqa: E501


DIFF_GEN_PROMPT = """
Documento original (encapsulado en triple tilde inversa):
```
{orig_doc}
```

Instrucciones de modificaciones (encapsulado en triple tilde inversa):
```
{mod_doc}
```

Documento consolidado:
"""


OPENAI_API_PARAMS_TEMPLATE: dict = {
    "model": "gpt-3.5-turbo-16k",
    "request_timeout": None,
    "max_tokens": 2000,
    "stream": False,
    "n": 1,
    "temperature": 0,
    "top_p": 1,
    "api_base": "",
}


def identify_article(modification_text: str, api_params: dict, oai_client: OpenAI) -> list:
    message_dicts = [
        {"role": "system", "content": DETECT_ARTICLE_MODIF_SYSTEM_PROMPT},
        {"role": "user", "content": modif_doc_prompt_prompt.format(mod_doc=modification_text)},
    ]
    response = oai_client.chat.completions.create(messages=message_dicts , **api_params) # type: ignore
    response_text = response.choices[0].message.content
    response = eval(response_text)
    assert isinstance(response, list), "Wrong output format:\n{response_text}"
    return response


def generate_diff_text(origin_text: str, mod_text: str, api_params: dict, oai_client: OpenAI) -> str:
    message_dicts = [
        {"role": "system", "content": DIFF_SYSTEM_PROMPT},
        {"role": "user", "content": DIFF_GEN_PROMPT.format(orig_doc=origin_text, mod_doc=mod_text)},
    ]
    response = oai_client.chat.completions.create(messages=message_dicts, **api_params) # type: ignore
    response_text = response.choices[0].message.content
    return response_text


def auto_generate_diff_text(
    origin_docs: dict,
    mod_docs: dict,
    diff_api_params: dict,
    id_article_api_params: dict,
    oai_client: OpenAI,
    verbose: bool = False,
) -> dict:
    diffed_docs = {}
    for mod_key, mod_doc in mod_docs.items():
        articles = identify_article(mod_doc, api_params=id_article_api_params, oai_client=oai_client)
        for article in articles:
            if verbose:
                print(mod_key, article)
            res = generate_diff_text(
                origin_text=origin_docs[article], mod_text=mod_doc, api_params=diff_api_params, oai_client=oai_client
            )
            if not res and verbose:
                logging.info(f"Article {article} not affected by modification {mod_key}")
            diffed_docs.update({article: res})
    return diffed_docs
