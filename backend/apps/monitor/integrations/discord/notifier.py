from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from apps.helpers.settings_vars import webhook_canal_testes

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
            self.color = "25009"
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
        return status_message_sent
