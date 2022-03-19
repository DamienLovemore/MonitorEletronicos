from apps.monitor.integrations.discord.notifier import DiscordNotify

# ---------------------------------------------------------------------------
# Arquivo responsável por rodar todos os bots de cada canal do Discord a cada
# tantos segundos. (Faz com que seja feito o monitoramento continua)
# E de manter o bot de assistência (ajuda) do canal do Discord online, e
# respondendo a usuários.
# ---------------------------------------------------------------------------

def run():
    # Placeholder
    DiscordNotify.send_message_test()
