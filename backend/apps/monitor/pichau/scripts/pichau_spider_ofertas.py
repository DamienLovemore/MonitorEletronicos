import os, json
from datetime import datetime
from time import sleep

import requests

from apps.produto.models import ProdutoEletrInf
from apps.helpers.settings_vars import url_pichau_ofertas, webhook_pichau_ofertas_ate_20, webhook_pichau_ofertas_ate_40, \
    webhook_pichau_ofertas_ate_60, webhook_pichau_ofertas_ate_100
from apps.helpers.logs import Logger
from apps.monitor.integrations.discord.notifier import DiscordNotify


# -----------------------------------------------------------------
# Arquivo responsável por olhar por ofertas nos produtos da pichau.
# -----------------------------------------------------------------

class PichauOfertas:
    def __init__(self):
        # A classe responsável por logar o precesso de obtenção
        # dos dados. (Para verificar depois se está funcionando)
        self.log = Logger(filename=os.path.basename(__file__))
        # O tipo de notificação que será mandada.
        # (1 - Novidades, 2 - Ofertas e 3 - Restock)
        self.tipo_notificacao = 2
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

            # Pega todos os dados da página
            script_page_data = page_request.content
            # Converte paraa json, para que seus dados possam ser acessados
            script_page_data = json.loads(script_page_data)

            # Pega os dados de todos os produtos da página
            products_data = script_page_data["data"]["products"]["items"]

            # Pega somente as ofertas dentre esses produtos
            # (Vem alguns que estão em destaque mas não são
            # ofertas)
            offers = []
            for product in products_data:
                # Produtos que não tem ofertas, vem com este
                # campo como null
                if product["special_price"] is not None:
                    offers.append(product)

            return offers
        # Se aconteceu algum erro ao pegar os dados, então loga isso.
        # Para posterior registro, e debug.
        except Exception as error:
            self.log.warning("Não foi possível fazer scraping da página de ofertas!")
            self.log.error(f"Erro extorado: \n{error}")
            self.log.info("\n")

    # Função responsável por cadastrar ofertas novas no banco.
    def criar_modelo(self, oferta: dict):
        # Armazena se esta oferta é uma oferta nova
        # (Não tinha antes no banco de dados)
        oferta_nova = False

        try:
            # Usa o get_or_create para cadastrar o novo modelo apenas se já não tiver ele no banco. Caso contrário ele não cria, ele só retorna o modelo.
            modelo_produto, criou = ProdutoEletrInf.objects.get_or_create(nome=oferta["nome"],
                                                                          imagem=oferta["imagem"],
                                                                          url_produto=oferta["url_produto"],
                                                                          perc_desconto=oferta["perc_desconto"],
                                                                          plataforma=oferta["plataforma"])

            # Se é um produto novo, muda o valor que retorna
            if criou:
                oferta_nova = True
        except ProdutoEletrInf.MultipleObjectsReturned:
            # Todo o tratamento e log para apagar os modelos duplicado do banco, deixando apenas o primeiro e logando o processo do tratamento e os modelos  duplicados encontrados
            # Pode ser encontrado produtos iguais em sites diferentes, não no mesmo site/plataforma.
            # --------------------------------------------------------------------------------------

            self.log.warning("Foram encontrados produtos duplicados (na mesma plataforma)!\n")

            modelos_produtos_duplicados = ProdutoEletrInf.objects.filter(nome=oferta["nome"],
                                                                         imagem=oferta["imagem"],
                                                                         url_produto=oferta["url_produto"],
                                                                         perc_desconto=oferta["perc_desconto"],
                                                                         plataforma=oferta["plataforma"])

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

        return oferta_nova

    # Função responsável por atualizar desconto de produtos existentes
    def atualizar_desconto_modelo(self, modelo_banco, oferta: dict):
        oferta_atualizada = False

        # Verifica o desconto salvo e o desconto atual, para ver
        # se tem que atualizar o modelo com o novo desconto
        desconto_salvo = modelo_banco.perc_desconto
        novo_desconto = oferta["perc_desconto"]

        if desconto_salvo != novo_desconto:
            oferta_atualizada = True

            # Atualiza o desconto do modelo com o novo valor,
            # e o salva no banco.
            modelo_banco.perc_desconto = novo_desconto
            modelo_banco.save()

        return oferta_atualizada

    # Função responsável por notificar as novas ofertas encontradas no Discord
    def notificar_ofertas_discord(self, itens_notificar: list):
        self.log.info("Notificando no Discord, ofertas novas")

        # Armazena a quantidade de mensagens mandadas,
        # para identificar limite de envio
        count = 0
        for item_notificar in itens_notificar:
            # Carrega a url do canal de ofertas da kabum para
            # a porcentagem de desconto referente a esse produto
            url_webhook_channel = ""
            if (item_notificar["perc_desconto"] >= 2) and (item_notificar["perc_desconto"] <= 20):
                url_webhook_channel = webhook_pichau_ofertas_ate_20
            elif (item_notificar["perc_desconto"] >= 21) and (item_notificar["perc_desconto"] <= 40):
                url_webhook_channel = webhook_pichau_ofertas_ate_40
            elif (item_notificar["perc_desconto"] >= 41) and (item_notificar["perc_desconto"] <= 60):
                url_webhook_channel = webhook_pichau_ofertas_ate_60
            elif item_notificar["perc_desconto"] > 60:
                url_webhook_channel = webhook_pichau_ofertas_ate_100

            # Cria a classe responsável por mandar a mensagem,
            # passando o conteúdo a ser notificado,
            notificador_discord = DiscordNotify(item_notificar, url_webhook_channel, self.tipo_notificacao,
                                                self.loja)

            # Manda a mensagem de fato
            notificador_discord.send_message()
            count += 1

            # Após notificar ve se chegou ao limite, para esperar
            # para enviar novamente
            # (30 mensagens a cada 60 segundos, é o limite do discord)
            if count % 30 == 0:
                sleep(60)

        self.log.info("Notificação no Discord foi concluída.\n")

    # Função responsável por verificar se deve cadastrar uma nova oferta,
    # ou se a oferta tem um desconto diferente e deve ser atualizada
    def verificar_criar_modelos(self, lista_ofertas: list):
        self.log.info("Verificando necessidade de criar modelos de ofertas!\n")

        # Armazena todos as novas ofertas encontras, ou que tiveram
        # descontos mudados. Para que sejam apitados no Discord
        offers_notify = []

        for oferta in lista_ofertas:
            # Verifica se o produto já existe
            try:
                oferta_existente = ProdutoEletrInf.objects.get(nome=oferta["nome"], imagem=oferta["imagem"],
                                                               url_produto=oferta["url_produto"],
                                                               plataforma=oferta["plataforma"])

                # Atualiza o produto caso tenha um novo desconto, e
                # se tiver manda para notificar
                oferta_atualizada = self.atualizar_desconto_modelo(oferta_existente, oferta)

                if oferta_atualizada:
                    offers_notify.append(oferta)
            # Senão existe, só cadastra a oferta
            except ProdutoEletrInf.DoesNotExist:
                oferta_nova = self.criar_modelo(oferta)

                # Se é uma oferta nova, adiciona para apitar no Discord.
                if oferta_nova:
                    offers_notify.append(oferta)

        # Notifica no Discord as novas ofertas encontradas
        self.notificar_ofertas_discord(offers_notify)

        self.log.info("Verificação concluída\n")

    # Função responsável pelo scraping, e por chamar as outras
    # funções, que criam modelos e notificam.
    def scraping(self):
        self.log.info("Procurando por informações nos produtos da página de ofertas\n")

        try:
            # Pega todos os produtos encontrados na página
            todas_ofertas = self.requisicao(url_pichau_ofertas)

            # Armazena todos as ofertas encontradas através
            # do scraping
            ofertas_encontradas = []

            # Olha por cada produto da ofertas
            for oferta in todas_ofertas:
                nome = oferta["name"]

                imagem = oferta["image"]["url_listing"]

                url_produto = oferta["url_key"]
                # Completa o resto da url, pois no href pode se omitir
                # a página inicial se tiver pegando recursos dela mesma
                url_produto = "https://www.pichau.com.br/" + url_produto

                # Pega o preço normal do produto
                preco_atual = float(oferta["price_range"]["minimum_price"]["final_price"]["value"])
                # Pega o preço dele a vista (preço normal - %12)
                preco_atual -= (12 / 100) * preco_atual
                # Arredonda o valor para ter duas casas depois da vírgula apenas
                preco = round(preco_atual, 2)
                # Formata o preço para ser algo como R$ xx,xx
                preco = str(preco)
                preco = preco.replace(".", ",")
                preco = "R$ " + preco

                preco_antigo = float(oferta["price_range"]["minimum_price"]["regular_price"]["value"])
                preco_antigo -= (12 / 100) * preco_antigo

                # Pega quantos porcento o preço atual, é do preço antigo
                perc_desconto = preco_atual * 100 / preco_antigo
                # Subtrai por 100, para ver quanto diminuiu
                perc_desconto = 100.0 - perc_desconto
                # Passa ele para positivo
                perc_desconto = abs(perc_desconto)
                # Deixa ele com apenas duas casas depois da virgula
                perc_desconto = round(perc_desconto, 2)

                estoque_total = oferta["mysales_promotion"]["qty_available"]
                estoque_vendido = oferta["mysales_promotion"]["qty_sold"]

                estoque_disponivel = abs(estoque_total - estoque_vendido)

                # Dicionário que guarda os dados encontrados no scraping
                # para um produto
                oferta = {
                    "nome": nome,
                    "imagem": imagem,
                    "url_produto": url_produto,
                    "preco": preco,
                    "perc_desconto": perc_desconto,
                    "estoque_disponivel": estoque_disponivel,
                    "plataforma": "pichau_ofertas"
                }

                # Adiciona a lista para verificar se deve criar ou não
                # no banco. (Se tiver achado antes, não cria)
                ofertas_encontradas.append(oferta)

            # Pega os produtos encontrados e vê se é algum que não
            # tinha sido encontrado antes.
            # Se for cria ele no banco, e notifica no discord.
            # (Produtos que já entraram em ofertas, mas agora tem
            # desconto diferente atualiza o modelo)
            self.verificar_criar_modelos(ofertas_encontradas)
        except Exception as error:
            self.log.error("Erro ao realizar scraping de produtos: {}!!".format(error))

        self.log.info("Fim da procura por informações nos produtos da página de ofertas\n")

    # Faz tudo o que precisa fazer, e no final loga o
    # tempo
    def get_items(self):
        start_time = datetime.now()
        self.log.info("Iniciando extração de dados: {}\n".format(start_time))

        self.scraping()

        end_time = datetime.now()
        # Calcula a diferença de tempo entre o momento que iniciou, e o momento que acabou.
        time_dif = end_time - start_time

        self.log.info("Tempo total para extração de dados: {}\n\n".format(time_dif))

def run():
    bot = PichauOfertas()
    bot.get_items()
