from django.db import models
from django.utils.safestring import mark_safe

# -------------------------------------------------------
# Django automaticamente cria um campo id. Que é inteiro,
# unico e que se auto-incrementa ao longo do tempo, ao
# criar um modelo.
# -------------------------------------------------------

# Modelo responsável por armazenar todas as informações
# sobre um produto eletrônico. (Menos preço, por questão
# de organização)
class ProdutoEletrInf(models.Model):
    # Define o nome da tabela que será salvo no banco esse modelo
    class Meta:
        db_table = "produto"

    # Armazena o nome do produto (máximo 100 caracteres)
    nome = models.CharField(max_length=100)
    # url da imagem desse produto
    imagem = models.CharField(max_length=255)
    # url do produto, mas com TextField pois ele não tem
    # limite de caracteres como o CharField
    url_produto = models.TextField()
    # O site em que esse produto foi encontrado (pichau,
    # kabum e etc) O verbose_name muda o nome que aparece
    # esse campo ao ve-lo no admin.
    plataforma = models.CharField(verbose_name="Site", max_length=100)
    # Armazena a data e o horário exato em que esse modelo
    # foi criado. (Atualizações futuras contam como edição)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    # Para produtos de restock, é usado para verificar
    # quando um produto importante não tinha estoque e
    # passa a ter para notificar no bot.
    # (identificado pela plataforma = nomesite_restock)
    tem_estoque = models.BooleanField(default=True, verbose_name="Estoque disponível")
    # Campo usado apenas pelos scripts de ofertas, para
    # que ele possa ver caso tenha um desconto diferente
    # do que tinha cadastrado para um mesmo produto, para
    # que ele possa notificar.
    # (blank=True, null=True - Campo não obrigatório)
    perc_desconto = models.FloatField(verbose_name="Porcentagem Desconto", blank=True, null=True)
    # Marca se esse produto deve ser monitorado ou não.
    # Para pode desativar monitoramento de produtos que
    # não importam. Padrão é True (Sim).
    # (Afeta monitoramento de histórico de preços, e
    # restock)
    monitorar = models.BooleanField(default=True, verbose_name="Monitorar")

    # Função responsável por carregar a imagem para ser
    # exibida no painel admin
    def imagem_produto(self):
        # Se tiver valor no campo imagem, prossegue
        # em carregar a imagem
        if self.imagem:
            # Carrega a tag html da imagem carregando
            # a url cadastrada
            return mark_safe('<img src="%s" style="width: 90px; height: 90px;" />' % self.imagem)
        else:
            return "Imagem não encontrada"

    # Retorna o que deve aparecer para identificar esse
    # produto ao retornar uma busca.
    def __str__(self):
        # Tudo em uma linha por performance. (Se tivesse
        # milhares de linha ia armazenar o retorno de
        # cada um em uma variavel só pra apagar depois
        return f"{self.nome}({self.plataforma})"

# Modelo responsável por representar o preço de um produto
# cadastrado, em um determinado dia e horário.
# (Para poder monitorar a variação do preço de um produto
# ao longo do tempo)
class PrecoInf(models.Model):
    # Define o nome da tabela que será salvo no banco esse modelo
    class Meta:
        db_table = "preco_produto"

    # Cria uma chave estrangeira que aponta para produto, ou seja
    # preco precisa ter um produto. Mas um produto pode ter varios
    # precos. O on_delete como CASCADE faz com que ao apagar um
    # produto todos os seus precos sejam apagos juntos com ele.
    # verbose_name faz com que no admin aparece um nome mais
    # descritivo.
    # (Django automaticamente coloca todas as chaves estrangeiras
    # no final na hora de criar a tabela para não dar erro)
    produto_referencia = models.ForeignKey(ProdutoEletrInf, on_delete=models.CASCADE, verbose_name="Produto referente")
    # Armazena como string o preco ao inves de float para facilitar
    # o uso na API, e na hora de notificar os produtos para pegar
    # seu valor. Também elimina problema de extorar limite de número
    # para preços grandes, e é utiliza menos memória armazenar um
    # número grande como sting. (Maioria dos usos é em string, e
    # se precisar é só converter)
    valor = models.CharField(max_length=50, verbose_name="Preço do produto")
    # Ao criar um modelo de preço ele automicamente pega a data e
    # hora de criação e coloca nesse campo. Para poder
    # posteriormente comprar os preços do produto em intervalos
    # de tempo. (Pega a data de criação e não de edição, pois esse
    # modelo não faz sentido e não deve ser editado)
    data_preco = models.DateTimeField(auto_now_add=True, verbose_name="Data do preço")

    # Retorna o que deve aparecer para identificar esse
    # preço ao retornar uma busca.
    def __str__(self):
        # Tudo em uma linha por performance. (Se tivesse
        # milhares de linha ia armazenar o retorno de
        # cada um em uma variavel só pra apagar depois
        return f"{self.produto_referencia} - {self.valor}({self.data_preco})"
