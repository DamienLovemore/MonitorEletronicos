from django.contrib import admin
from .models import ProdutoEletrInf, PrecoInf

# -------------------------------------------------------
# Arquivo responsável por registrar (ligar) os modelos
# (tabelas), ao painel admin e assim podermos acessa-las,
# edita-las e apagar elas por lá.
# -------------------------------------------------------

# Configurações que determinam como esse modelo deve se
# apresentar e comportam quando tiver sendo acessa-da
# através do painel admin.
class ProdutoEletrInfAdmin(admin.ModelAdmin):
    # O modelo que essa configuração se aplica
    model = ProdutoEletrInf
    # Campos que devem apenas ser vistos, e não
    # alterados no painel admin.
    readonly_fields = ("plataforma", "data_criacao", "tem_estoque", "perc_desconto")
    # Campos que podem ser mostrados ao olhar
    # por esse modelo no painel admin.
    list_display = ("nome", "imagem_produto", "url_produto", "plataforma", "data_criacao", "tem_estoque", "perc_desconto", "monitorar")
    # Campos que podem ser usados para filtrar
    # resultados encontrados na busca.
    list_filter = ("monitorar", "plataforma", "data_criacao", "perc_desconto")
    # Os campos desse modelo (tabela) que podem ser
    # usados para pesquisar por esse modelo.
    # (Nome dele, e o site que foi encontrado)
    search_fields = ("nome", "plataforma")

class PrecoInfAdmin(admin.ModelAdmin):
    model = PrecoInf
    readonly_fields = ("produto_referencia", "data_preco")
    list_display = ("produto_referencia", "valor", "data_preco")
    list_filter = ("data_preco", "valor")
    search_fields = ("produto_referencia", "data_preco")


# Liga as nossas configurações do painel admin a esta classe.
# E a torna acessível pelo admin também.
admin.site.register(ProdutoEletrInf, ProdutoEletrInfAdmin)
admin.site.register(PrecoInf, PrecoInfAdmin)
