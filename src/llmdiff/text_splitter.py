import re

footer_pattern = r"\(\d+\) (DO [LC] \d+ de \d{1,2}\.\d{1,2}\.\d{4}, p\. \d+\.)"
article_split_pattern = r"^(?=Artículo \d+$)"
wrong_new_lines_pattern = r"(?<=[a-z,])\n(?=[a-z](?!\)))"
parentheses_enum_fix = r"(?<=[\w\d])\n(?=\))"
parentheses_split_pattern = r"^(?=[\d]+\)$\n)"


def clean_source_text(source_text: str):
    source_text = re.sub(wrong_new_lines_pattern, " ", source_text)
    source_text = re.sub(footer_pattern, "\n", source_text)
    source_text = re.sub(wrong_new_lines_pattern, " ", source_text)
    source_text = re.sub(parentheses_enum_fix, "", source_text)
    return source_text


def split_by_article(source_text: str) -> dict:
    # First block is preamble
    articles = re.split(article_split_pattern, source_text, flags=re.MULTILINE)[1:]
    articles = [article.strip() for article in articles]
    articles_dict = {f"articulo_{i+1}": art for i, art in enumerate(articles)}
    return articles_dict


def split_by_parentheses_enum_list(source_text: str):
    # First block is preamble
    elems = re.split(parentheses_split_pattern, source_text, flags=re.MULTILINE)[1:]
    elems = [elem.strip() for elem in elems]
    elems_dict = {i: art for i, art in enumerate(elems)}
    return elems_dict
