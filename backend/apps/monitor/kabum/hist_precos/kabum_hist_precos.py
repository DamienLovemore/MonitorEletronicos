import os, threading
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

from django.conf import settings
from django.utils.timezone import make_aware

from apps.produto.models import ProdutoEletrInf, PrecoInf
from apps.helpers.logs import Logger


# -----------------------------------------------------------------
# Arquivo reponsável por uma vez por dia olhar na página de cada
# produto, e registrar o preço daquele produto naquele dia no
# banco de dados.
# -----------------------------------------------------------------

class KabumHistPrecos:
    def __init__(self):
        # A classe responsável por logar o precesso de obtenção
        # dos dados. (Para verificar depois se está funcionando)
        self.log = Logger(filename=os.path.basename(__file__))

    # Faz a requisição a página do produto
    # Para pegar seus dados
    def requisicao(self, url: str):
        product_price = None

        try:
            # Headers usado na requisição para fasilficar que é um
            # usuário acessando a página, e não um bot
            headers = {
                'authority': 'www.kabum.com.br',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'upgrade-insecure-requests': '1',
                'dnt': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7'
            }

            # Tenta fazer uma requisição a página para pegar seu conteúdo
            # usando headers para se passar por um usuário, e com timeout
            # de 15 segundos para o servidor não ficar segurando a
            # requisição para sempre ao tentar evitar bots.
            page_request = requests.get(url, headers=headers, timeout=15)

            # Pega o conteúdo da página, e converte para uma coisa que o
            # python entenda. (Usa o parser html, pois a resposta da
            # requisição é uma página html)
            page_content = BeautifulSoup(page_request.content, "html.parser")

            # Pega o elemento que contém o preço
            product_price = page_content.find("h4", attrs={"itemprop": "price"})

            if product_price is not None:
                # Pega o texto que está nesse elemento
                # Formato válido: R$ xx,xx
                product_price = str(product_price.next_element)
            # Senão conseguiu pegar o preço, verificar se o
            # produto não tem estoque
            else:
                formulario_sem_estoque = page_content.find("div", attrs={"id": "formularioProdutoIndisponivel"})

                # Se não achou o preço, e esse produto tem estoque
                # Então disparar um  erro
                if formulario_sem_estoque is None:
                    # Marca que o produto não existe mais, para ser
                    # removido
                    titulo_pagina = str(page_content.find("title").next_element)
                    if titulo_pagina == "404 - Página não encontrada":
                        product_price = -1

                    raise Exception("Não achou preço, mas também não pode confirmar que ele não tem estoque")

        # Se aconteceu algum erro ao pegar os dados, então loga isso.
        # Para posterior registro, e debug.
        except Exception as error:
            self.log.warning(f"Não foi possível acessar a página do produto: {url}!")
            self.log.error(f"Erro extorado: \n{error}")
            self.log.info("\n")

        return product_price

    # Função responsável por cadastrar novos preços
    # para um produto, e marcar a data de hoje
    def criar_modelos(self, preco: str, produto):
        self.log.info(f"Criando novo modelo de preço para produto com id: {produto.pk}!")

        try:
            # Usa o get_or_create para cadastrar o novo modelo apenas se já não tiver ele no banco. Caso contrário ele não cria, ele só retorna o modelo.
            # Pega a data-hora atual, e coloca fuso-horário nela da configuração que
            # está colocada no settings do Django.
            data_hora_atual = make_aware(datetime.now())
            modelo_preco, criou = PrecoInf.objects.get_or_create(produto_referencia=produto, valor=preco,
                                                                 data_preco=data_hora_atual)
        except ProdutoEletrInf.MultipleObjectsReturned:
            self.log.warning("Foram encontrados preços duplicados (na mesma plataforma)!\n")

            modelos_precos_duplicados = PrecoInf.objects.filter(produto_referencia=produto, valor=preco,
                                                                data_preco=data_hora_atual)

            self.log.info(
                "A quantidade de preços duplicados encontrados foram {}".format(len(modelos_precos_duplicados)))

            self.log.info("Os preços duplicados encontrados foram: ")

            cont_modelo_atual = -1
            for modelo_duplicado in modelos_precos_duplicados:
                cont_modelo_atual += 1

                if cont_modelo_atual == 0:  # Não apaga o primeiro modelo, o mantém no banco. Apenas o loga
                    # Loga o modelo do banco de dados, com os seus campos.
                    self.log.info(modelo_duplicado)

                    # Pelo fato de get_or_create ter crashado e não ter feito o get com as informações, fazemos aqui manualmente
                    modelo_preco = modelo_duplicado
                    criou = False
                # No penúltimo tênis apagado, em seu log deve se deixar um espaço por questões de estética e facilidade de leitura da log.
                elif cont_modelo_atual == len(modelos_precos_duplicados) - 1:
                    self.log.info(modelo_duplicado)
                    self.log.info("")

                    modelo_duplicado.delete()  # Apaga o modelo duplicado do banco
                else:
                    self.log.info(modelo_duplicado)

                    modelo_duplicado.delete()

            self.log.warning(
                "Preços duplicados do banco foram apagados com sucesso! (Somente o primeiro que foi encontrado foi mantido)\n")

    # Função responsável por registrar o preço desse produto hoje
    def registrar_preco_hoje(self, produto):
        # Pega o preço atual do programa
        preco_atual = self.requisicao(produto.url_produto)

        # Cria um novo modelo de preço para este produto,
        # com o preço atual e data de hoje.
        # (Se ele conseguiu pegar o preço atual)
        if preco_atual is not None:
            self.criar_modelos(preco_atual, produto)
        # Se o produto não existe mais, apaga ele
        elif preco_atual == -1:
            produto.delete()

    # Função responsável pelo scraping, e por chamar as outras
    # funções que fazem o resto que precisa com esses dados
    def scraping(self):
        self.log.info("Procurando por informações nas páginas dos produtos de de kabum_novidades\n")

        # Pega todos os produtos do banco de dados que sejam
        # de kabum_novidades, e que seu monitoramento não
        # tenha sido desativado
        lista_produtos = ProdutoEletrInf.objects.filter(plataforma="kabum_novidades", monitorar=True)

        # Só procede caso tenha produtos no banco para terem
        # seus preços monitorados
        if len(lista_produtos) > 0:
            # Percorre cada produto para ver se tem que atualizar
            # seu preço. (Checa cada produto uma vez por dia)
            for produto in lista_produtos:
                # Pega todos os preços que são pertencentes a este produto,
                # e dentre esses pega apenas o mais recente. (Pela data,
                # para ver se já foi rodado hoje)
                try:
                    ultimo_preco = PrecoInf.objects.filter(produto_referencia=produto).latest("data_preco")

                    # Se o último preço foi pego em um dia antes de hoje,
                    # ele deve registrar o preço desse produto hoje
                    if ultimo_preco.data_preco.date() < date.today():
                        threading.Thread(target=self.registrar_preco_hoje, args=(produto,)).start()

                # Caso ainda não tenha nenhum preço cadastrado para esse
                # produto
                except PrecoInf.DoesNotExist:
                    threading.Thread(target=self.registrar_preco_hoje, args=(produto,)).start()

        self.log.info("Fim da procura por nas páginas dos produtos de de kabum_novidades\n")

    # Faz tudo o que precisa fazer, e no final loga o
    # tempo
    def get_items(self):
        start_time = datetime.now()
        self.log.info("Iniciando extração de dados: {}\n".format(start_time))

        # Realiza o scraping na página dos produtos, e
        # faz o que precisa com os dados coletados
        self.scraping()

        end_time = datetime.now()
        # Calcula a diferença de tempo entre o momento que iniciou, e o momento que acabou.
        time_dif = end_time - start_time

        self.log.info("Tempo total para extração de dados: {}\n\n".format(time_dif))
