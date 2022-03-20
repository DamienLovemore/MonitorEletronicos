import continuous_threading
from time import sleep

#Kabum
from apps.monitor.kabum.novidades.kabum_novidades_games import KabumNovidadesGames
from apps.monitor.kabum.novidades.kabum_novidades_hardware import KabumNovidadesHardware
from apps.monitor.kabum.novidades.kabum_novidades_computadores import KabumNovidadesComputadores
from apps.monitor.kabum.novidades.kabum_novidades_smartphones import KabumNovidadesSmartphones

# ---------------------------------------------------------------------------
# Arquivo responsável por rodar todos os bots de cada canal do Discord a cada
# tantos segundos. (Faz com que seja feito o monitoramento continua)
# E de manter o bot de assistência (ajuda) do canal do Discord online, e
# respondendo a usuários.
# ---------------------------------------------------------------------------

def task_kabum_novidades_games():
    kabum_novidades_games = KabumNovidadesGames()
    while True:
        kabum_novidades_games.get_items()
        sleep(8)

def task_kabum_novidades_hardware():
    kabum_novidades_hardware = KabumNovidadesHardware()
    while True:
        kabum_novidades_hardware.get_items()
        sleep(8)

def task_kabum_novidades_computadores():
    kabum_novidades_computadores = KabumNovidadesComputadores()
    while True:
        kabum_novidades_computadores.get_items()
        sleep(8)

def task_kabum_novidades_smartphones():
    kabum_novidades_smartphones = KabumNovidadesSmartphones()
    while True:
        kabum_novidades_smartphones.get_items()
        sleep(8)

def run():
    # continuous_threading é uma biblioteca especializa em rodar threads
    # continuamente. Ela possue por padrão diversos recursos, e ferramentas
    # para otimização de threads que rodam em loop. E mecanismo para que ao
    # encerrar as tasks seus recursos sejam liberados corretamente.

    ### Kabum ###
    continuous_threading.Thread(target=task_kabum_novidades_games).start()
    continuous_threading.Thread(target=task_kabum_novidades_hardware).start()
    continuous_threading.Thread(target=task_kabum_novidades_computadores).start()
    continuous_threading.Thread(target=task_kabum_novidades_smartphones).start()
