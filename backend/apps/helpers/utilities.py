# Função responsável por pegar a url do produto, e identificar qual
# categoria ele pertence. Para enviar para o canal certo do Discord.
def indentificar_categoria_produto(url_produto: str):
    # Por padrão é perifericos, caso não
    # enquadrar em nenhuma categoria
    categoria = "perifericos"

    # Declara o conjunto de palavras-chaves para serem usados para
    # identificar cada categoria
    keywords_hardware = ["processador", "placa-mae", "memoria", "placa-de-video", "hd-", "ssd-", "gabinete", "fonte",
                         "cooler", "ventoinhas", "pasta-termica", "placa-de-som", "gravador"]
    keywords_perifericos = ["caixa-de-som", "teclado", "fone-de-ouvido", "headset", "kit-teclado-e-mouse-", "mouse-",
                            "mousepad", "cabo", "impressora", "webcam", "pendrive"]
    keywords_computadores = ["computador"]
    keywords_notebooks = ["notebook", "notebook-gamer", "base-para-notebook"]

    # Verifica se a url do produto se enquadra em alguma das
    # palavras-chaves dessa categoria.
    # Se sim, retorna essa a url do Discord dessa categoria.
    # ------------------------------------------------------

    for kw in keywords_hardware:
        if kw in url_produto:
            categoria = "hardware"

    for kw in keywords_perifericos:
        if kw in url_produto:
            categoria = "perifericos"

    for kw in keywords_computadores:
        if kw in url_produto:
            categoria = "computadores"

    for kw in keywords_notebooks:
        if kw in url_produto:
            categoria = "notebooks"

    # Caso não se enquadrar em nada, retorna a url como
    # periférico.(Que é o mais genérico)
    return categoria
