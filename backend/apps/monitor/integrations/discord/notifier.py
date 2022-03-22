from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from apps.helpers.settings_vars import webhook_canal_testes

# ---------------------------------------------------------------------------
# Arquivo responsável por fazer a integração com o sistema de mensagens do
# discord, possibilitando mandar mensagens em várias canais diferentes.
# E costomizar o conteúdo dessas mensagens da meneira que for necessário
# ---------------------------------------------------------------------------

class DiscordNotify:
    def __init__(self, item_notificar, url_webhook, tipo_notificacao, plataforma):
        # Pega o conteúdo da mensagem que será enviada
        self.item = item_notificar
        # Inicia conecção com o canal discord dessa url
        self.webhook = DiscordWebhook(url=url_webhook)
        # Pega a data e horário que a classe foi criada
        # para notificar. (Caso precise depois)
        self.timestamp = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime("%d/%m/%Y %H:%M:%S")
        self.tipo_notificacao = tipo_notificacao

        # Pega o nome da loja, para assim definir qual
        # será a cor da mensagem a ser enviada.
        # (Cada loja tem uma cor diferente, para
        # identificar de qual loja veio)
        # ---------------------------------------------

        if plataforma == "kabum":
            # Código Hexadecimal para identificar cor
            # Exemplo: #0061b1 -> 0x0061b1 (Cor Azul)
            self.color = 0x0061b1
        # Se for uma loja desconhecida, coloca como cor
        # da mensagem preto.
        else:
            self.color = 0x9695a0

    # Manda uma mensagem de teste para o canal de testes
    # do Discord. Para ver se está funcionando a
    # integração corretamente
    @staticmethod
    def send_message_test():
        # Discord Embed é o conteúdo da mensagem que será
        # enviado através do Discord Webhook.
        # title = Título da mensagem
        # color = Cor da mensagem. (Fica no lado esquerdo)
        message_content = DiscordEmbed(title="Hello World :)".upper(), color=0x9695a0)
        # Coloca o conteúdo a ser enviado, na classe
        # responsável por mandar mensagem pro Discord.
        webhook = DiscordWebhook(url=webhook_canal_testes)
        webhook.add_embed(message_content)
        # Execute manda o conteúdo da mensagem ligada
        # a esse webhook em seu canal que foi
        # especificado.
        # (Posição 0 guarda o status da requsição, se
        # for 200 deu certo)
        status_message_sent = webhook.execute()
        status_message_sent = status_message_sent.status_code

        return status_message_sent

    # Função responsável por mandar a notificação dos
    # produtos nos canais correspondentes
    def send_message(self):
        # Foram separados por código tipos de mensagem diferentes que se adequam a cada umas das
        # necessidades de nossos scripts. E foram criados três tipos de mensagens genericas
        # que se encaixam para eles.
        # --------------------------------------------------------------------------------------

        # Notificar novidade (lançamento)
        if self.tipo_notificacao == 1:
            # Cria o conteúdo da mensagem com o título e cor
            # passados
            message_content = DiscordEmbed(self.item["nome"].upper(), color=self.color)

            # Coloca a imagem de fundo nessa mensagem
            message_content.set_thumbnail(url=self.item["imagem"])

            # Coloca o link de acesso para o produto
            # (Aparece como o nome do produto, mais ao clicar
            # vai para a página desse produto)
            message_content.add_embed_field(name="Produto:", value=(f"[{self.item['nome']}]({self.item['url_produto']})"), inline=False)

            # O preço do produto
            # Formatado para ser: R$ xx,xx
            message_content.add_embed_field(name="Valor:", value=self.item["preco"], inline=False)

            # Adiciona o conteúdo da mensagem, a classe
            # responsável por enviar a mensagem
            self.webhook.add_embed(message_content)

            # Execute manda o conteúdo da mensagem ligada
            # a esse webhook em seu canal que foi
            # especificado.
            # (Posição 0 guarda o status da requsição, se
            # for 200 deu certo)
            status_message_sent = self.webhook.execute()
            status_message_sent = status_message_sent.status_code

            return status_message_sent
