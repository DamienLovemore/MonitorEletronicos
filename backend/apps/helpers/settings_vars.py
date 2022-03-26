# --------------------------------------------------------------------------
# Arquivo responsável por armazenar todas as urls, palavras-chaves, webhooks
# e outras informações utilizadas pelos bots. Para que essas informações não
# fiquem expostas e declaradas explicitamente nos bots, para que caso o
# código vaze. Eles não saibam os critérios usados, e nem de onde está sendo
# pego as informações.
# --------------------------------------------------------------------------

# Canal de testes de Webhook
webhook_canal_testes = "https://discord.com/api/webhooks/954793840865329172/GIFcJ0ugIW8TMJuDHzRDkLbb6uBmNGPZKk8MPiD-M6V62Evc7o1_4zPCzm7VOkwtD6Ti"

### KABUM ###

# -> Novidades
webhook_kabum_novidades = "https://discord.com/api/webhooks/955057968515276812/Aq8CM42XGzAHyD_Wj07WOMUEK5lhUB7yOfe3K-ignpdyb_KRnJmbd3KBhgLlThV0CPGA"
url_kabum_novidades_games = "https://www.kabum.com.br/gamer?page_number={}&page_size=100&facet_filters=&sort=-date_product_arrived"
url_kabum_novidades_smartphones = "https://www.kabum.com.br/celular-smartphone?page_number={}&page_size=100&facet_filters=&sort=-date_product_arrived"
url_kabum_novidades_computadores = "https://www.kabum.com.br/computadores?page_number={}&page_size=100&facet_filters=&sort=-date_product_arrived"
url_kabum_novidades_hardware = "https://www.kabum.com.br/hardware?page_number={}&page_size=100&facet_filters=&sort=-date_product_arrived"

# -> Ofertas
webhook_kabum_ofertas_ate_20 = "https://discord.com/api/webhooks/955864873986834464/unSiirruRGB6_TeaGnffSQaSJUSo1JZDZx-16wf7hLRbgNbqkMLA2T9NAk4-Uky1kZwz"
webhook_kabum_ofertas_ate_40 = "https://discord.com/api/webhooks/955865215692574790/iAJB3_ES8jz3kGZc1dB_q8UGAGCX_PIzI5J8_XlmbhhMuiJge_UApHOEIOrhoKT4xyxi"
webhook_kabum_ofertas_ate_60 = "https://discord.com/api/webhooks/955865893336932362/Wxyyze8EEWwegNNlfyPhJbwmpC8vgY2doBqkvgSopjVAxHRm6lpHFx-Quww2bO8v-wrI"
webhook_kabum_ofertas_ate_100 = "https://discord.com/api/webhooks/955866142851862588/1B3B9zmR03nPd7oWH4gJKzamlyfvIqRKd9EV9PGqqZ5etlol70_8-qdcnysobgryyMqm"

url_kabum_ofertas = "https://www.kabum.com.br/destaques?page_number=1&page_size=100&facet_filters=eyJjYXRlZ29yeSI6WyJDb21wdXRhZG9yZXMiLCJDZWx1bGFyICYgU21hcnRwaG9uZSIsIkdhbWVzIiwiSGFyZHdhcmUiXX0=&sort=-date_product_arrived"

# -> Restock
keywords_kabum_restock = ["gamer", "notebook", "computador", "placa-de-video", "processador", "nvidia", "rtx", "amd",
                          "apple", "smartphone", "nintendo", "gtx", "intel-core"]

### PICHAU ###

# -> Novidades
webhook_pichau_novidades = "https://discord.com/api/webhooks/957244975484125224/t_iHYegCznduC4t6wyKDwzooW3AnYSxqTHoYf7I-u9pSlTf4vZ8J0adHL2Xbrj391sj9"
url_pichau_novidades_hardware = "https://www.pichau.com.br/hardware"
url_pichau_novidades_perifericos = "https://www.pichau.com.br/perifericos"
url_pichau_novidades_computadores = "https://www.pichau.com.br/computadores"
url_pichau_novidades_notebooks = "https://www.pichau.com.br/notebooks"
keywords_pichau_restock = ["placa-de-video", "rtx", "gtx", "amd", "processador", "gamer", "notebook", "ssd", "razer",
                           "ryzen", "intel"]
