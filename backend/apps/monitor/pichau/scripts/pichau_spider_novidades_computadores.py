import os
from datetime import datetime

from apps.helpers.settings_vars import webhook_pichau_novidades_computadores, url_pichau_novidades_computadores
from apps.helpers.logs import Logger

from apps.monitor.pichau.novidades.base import PichauNovidades

# -----------------------------------------------------------------
# Arquivo responável por fazer o scraping da página de novidades na
# Pichau na categoria de computadores, e apitar produtos novos
# encontrados.
# -----------------------------------------------------------------

class PichauNovidadesComputadores:
    def __init__(self):
        # A url da página onde seram pegos os dados
        self.url = url_pichau_novidades_computadores
        # A classe responsável por logar o precesso de obtenção
        # dos dados. (Para verificar depois se está funcionando)
        self.log = Logger(filename=os.path.basename(__file__))
        # A classe que faz todo o processo de scraping, criação
        # de modelos e notificação no Discord.
        self.novidades = PichauNovidades(self.log, webhook_pichau_novidades_computadores)

    # Faz tudo o que precisa fazer, e no final loga o
    # tempo
    def get_items(self):
        start_time = datetime.now()
        self.log.info("Iniciando extração de dados: {}\n".format(start_time))

        self.novidades.scraping(self.url)

        end_time = datetime.now()
        # Calcula a diferença de tempo entre o momento que iniciou, e o momento que acabou.
        time_dif = end_time - start_time

        self.log.info("Tempo total para extração de dados: {}\n\n".format(time_dif))


def run():
    bot = PichauNovidadesComputadores()
    bot.get_items()
