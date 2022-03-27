import requests, json
from time import sleep
from bs4 import BeautifulSoup

from apps.produto.models import ProdutoEletrInf
from apps.helpers.settings_vars import keywords_pichau_restock
from apps.monitor.integrations.discord.notifier import DiscordNotify

# -----------------------------------------------------------------
# Arquivo com a estrutura base usado em comum por todos os scripts(
# ou tasks) de monitoramento de novidades. (E também marca produtos
# valiosos para restock)
# -----------------------------------------------------------------

class PichauNovidades:
    def __init__(self, log, discord_webhook: str):
        # Guarda a referência da classe que vai ser responsável por
        # registrar as operações feitas
        self.log = log
        # A url do webhook que aponta para o canal onde deve ser
        # mandado essa notificação
        self.url_discord = discord_webhook
        # O tipo de notificação que será mandada.
        # (1 - Novidades, 2 - Ofertas e 3 - Restock)
        self.tipo_notificacao = 1
        # A loja que pertence os produtos que serão mandados a
        # notificação
        self.loja = "pichau"

    # Função responsável por fazer a requisição
    # a página
    def requisicao(self, url: str):
        try:
            # Headers usado na requisição para fasilficar que é um
            # usuário acessando a página, e não um bot
            headers = {
                'authority': 'www.pichau.com.br',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
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

            # Pega todos os dados da página
            script_page_data = page_content.find("script", attrs={"id": "__NEXT_DATA__"})
            # Converte paraa json, para que seus dados possam ser acessados
            script_page_data = json.loads(script_page_data.next_element)

            # Pega os dados de todos os produtos da página
            products = script_page_data["props"]["pageProps"]["pageData"]["content"]["products"]["items"]

            return products
        # Se aconteceu algum erro ao pegar os dados, então loga isso.
        # Para posterior registro, e debug.
        except Exception as error:
            self.log.warning("Não foi possível fazer scraping da página de novidades!")
            self.log.error(f"Erro extorado: \n{error}")
            self.log.info("\n")

    # Função responsável pelo scraping, e por chamar as outras
    # funções, que criam modelos e notificam.
    def scraping(self, url: str):
        self.log.info("Procurando por informações nos produtos da página de novidades\n")

        try:
            # Pega todos os produtos encontrados na página
            todos_produtos = self.requisicao(url)

            # Armazena todos os produtos encontrados através
            # do scraping
            produtos_encontrados = []

            # Olha por cada produto da página
            for produto in todos_produtos:
                nome = produto["name"]

                imagem = produto["image"]["url_listing"]

                url_produto = produto["url_key"]
                # Completa o resto da url, pois no href pode se omitir
                # a página inicial se tiver pegando recursos dela mesma
                url_produto = "https://www.pichau.com.br/" + url_produto

                # Pega o preço normal do produto
                preco = float(produto["price_range"]["minimum_price"]["regular_price"]["value"])
                # Pega o preço dele a vista (preço normal - %12)
                preco -= (12 / 100) * preco
                # Arredonda o valor para ter duas casas depois da vírgula apenas
                preco = round(preco, 2)
                # Formata o preço para ser algo como R$ xx,xx
                preco = str(preco)
                preco = preco.replace(".", ",")
                preco = "R$ " + preco

                # Dicionário que guarda os dados encontrados no scraping
                # para um produto
                produto_eletr = {
                    "nome": nome,
                    "imagem": imagem,
                    "url_produto": url_produto,
                    "preco": preco,
                    "plataforma": "pichau_novidades"
                }

                # Adiciona a lista para verificar se deve criar ou não
                # no banco. (Se tiver achado antes, não cria)
                produtos_encontrados.append(produto_eletr)

            # Pega os produtos encontrados e vê se é algum que não
            # tinha sido encontrado antes.
            # Se for criar ele no banco, e notifica no discord.
            self.criar_modelos(produtos_encontrados)
            
        except Exception as error:
            self.log.error("Erro ao realizar scraping de produtos: {}!!".format(error))

        self.log.info("Fim da procura por informações nos produtos da página de novidades\n")

    # Função responsável para verificar se um produto é
    # valioso o suficente para ser marcado como restock.
    # (Para monitorar esse produto quando tiver estoque
    # novamente)
    def check_keywords(self, url_produto: str):
        # Converte tudo para minusculo para não dar
        # problema na hora da comparacao
        url = url_produto.lower()

        # Armazena a quantidade de palavras-chave que
        # foram encontradas na url
        count = 0
        # Verifica cada palavra-chave
        for kw in keywords_pichau_restock:
            if kw in url:
                count += 1

        # Retorna verdadeiro caso a url do produto
        # tenha alguma das palavra-chaves
        return True if count > 0 else False

    # Código base que é usado tenta para criar modelos
    # de novidades, quanto de restock.
    # Para evitar repetição, e facilitar manutenção.
    def base_criar_modelos(self, product: dict, plataforma: str):
        # Armazena se esse produto é um produto novo
        # (Não tinha antes no banco de dados)
        produto_novo = False

        # Se for restock, antes de tentar criar deve-se verificar se
        # esse produto é valioso o suficiente para ser criado
        if plataforma == "pichau_restock":
            # Se não for importante para restock, então nem continua
            if self.check_keywords(product["url_produto"]) is False:
                return produto_novo

        try:
            # Usa o get_or_create para cadastrar o novo modelo apenas se já não tiver ele no banco. Caso contrário ele não cria, ele só retorna o modelo.
            modelo_produto, criou = ProdutoEletrInf.objects.get_or_create(nome=product["nome"],
                                                                          imagem=product["imagem"],
                                                                          url_produto=product["url_produto"],
                                                                          plataforma=plataforma)

            # Se é um produto novo, muda o valor que retorna
            if criou:
                produto_novo = True
        except ProdutoEletrInf.MultipleObjectsReturned:
            # Todo o tratamento e log para apagar os modelos duplicado do banco, deixando apenas o primeiro e logando o processo do tratamento e os modelos  duplicados encontrados
            # Pode ser encontrado produtos iguais em sites diferentes, não no mesmo site/plataforma.
            # --------------------------------------------------------------------------------------

            self.log.warning("Foram encontrados produtos duplicados (na mesma plataforma)!\n")

            modelos_produtos_duplicados = ProdutoEletrInf.objects.filter(nome=product["nome"],
                                                                         imagem=product["imagem"],
                                                                         url_produto=product["url_produto"],
                                                                         plataforma=plataforma)

            self.log.info(
                "A quantidade de produtos duplicados encontrados foram {}".format(len(modelos_produtos_duplicados)))

            self.log.info("Os produtos duplicados encontrados foram: ")

            cont_modelo_atual = -1
            for modelo_duplicado in modelos_produtos_duplicados:
                cont_modelo_atual += 1

                if cont_modelo_atual == 0:  # Não apaga o primeiro modelo, o mantém no banco. Apenas o loga
                    # Loga o modelo do banco de dados, com os seus campos.
                    self.log.info(modelo_duplicado)

                    # Pelo fato de get_or_create ter crashado e não ter feito o get com as informações, fazemos aqui manualmente
                    modelo_produto = modelo_duplicado
                    criou = False
                # No penúltimo tênis apagado, em seu log deve se deixar um espaço por questões de estética e facilidade de leitura da log.
                elif cont_modelo_atual == len(modelos_produtos_duplicados) - 1:
                    self.log.info(modelo_duplicado)
                    self.log.info("")

                    modelo_duplicado.delete()  # Apaga o modelo duplicado do banco
                else:
                    self.log.info(modelo_duplicado)

                    modelo_duplicado.delete()

            self.log.warning(
                "Produtos duplicados do banco foram apagados com sucesso! (Somente o primeiro que foi encontrado foi mantido)\n")

        return produto_novo

    # Função responsável por cadastrar produtos de
    # novidades e marcar eles para restock. Caso não
    # tenham sido encontrados antes.
    # (Apita no discord caso seja coisa nova)
    def criar_modelos(self, products_list: list):
        self.log.info("Verificando necessidade de criar modelos de produtos!")

        # Armazena todos os novos produtos encontrados,
        # para depois notificar no discord.
        products_notify = []

        try:
            # Olha por cada produto encontrado; Primeiro olha por novidades
            for product in products_list:
                # Faz a verificação se deve criar modelo para novidades
                produto_novo = self.base_criar_modelos(product, "pichau_novidades")

                # Coloca na fila para apitar no Discord, apenas produtos
                # novos da categoria de novidades
                if produto_novo:
                    products_notify.append(product)

                # Faz a verificação se deve criar modelo para restock
                # (Apenas produtos interessantes para restock)
                self.base_criar_modelos(product, "pichau_restock")
        except Exception as error:
            self.log.error(f"Erro ao criar modelos dos produtos: {error}!")

        # Caso encontrou novidade, então ele notifica no canal do
        # Discord os produtos encontrados. (No canal de novidades
        # da Kabum)
        if len(products_notify) > 0:
            # Armazena a quantidade de mensagens mandadas,
            # para identificar limite de envio
            count = 0
            # Para cada produto no discord realiza uma notificação
            self.log.info("Notificando no Discord, produtos novos")
            for product in products_notify:
                self.notificar_discord(product)
                count += 1

                # Após notificar ve se chegou ao limite, para esperar
                # para enviar novamente
                # (30 mensagens a cada 60 segundos, é o limite do discord)
                if count % 30 == 0:
                    sleep(60)
            self.log.info("Notificação no Discord foi concluída.")

        self.log.info("Verificação concluída\n")

    # Função responsável por enviar a notificação do novo
    # produto encontrado no canal de novidades da Kabum.
    # (No nosso servidor Discord)
    def notificar_discord(self, item_notificar):
        try:
            # Cria a classe responsável por mandar a mensagem,
            # passando o conteúdo a ser notificado,
            notificador_discord = DiscordNotify(item_notificar, self.url_discord, self.tipo_notificacao, self.loja)

            # Manda a mensagem de fato
            notificador_discord.send_message()

        except Exception as error:
            self.log.warning(f"Falha ao notificar o produto {item_notificar} no discord.")
            self.log.error(f"Erro extorado: \n{error}")
            self.log.info("\n")
