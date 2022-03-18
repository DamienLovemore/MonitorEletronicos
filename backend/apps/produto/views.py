from rest_framework import generics
from .models import ProdutoEletrInf, PrecoInf
from .serializers import ProdutoEletrInfSerializer, PrecoInfSerializer
# Usa o as para dar um outro nome e não dar conflito com o rest_framework
# de verdade. (Não o filtro django dele)
from django_filters import rest_framework as filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.core import exceptions as django_exceptions
from django.http import Http404

# -------------------------------------------------------------------------
# Todas as APIS e sites que podem ser acessados dentro do app produto
# (Posteriormente são linkadas a uma url, para que ao acessar ela seja
# carregado essa API ou site)
# -------------------------------------------------------------------------

# Página para listar todos os produtos que foram cadastrados, para que eles
# possam ser visualizados.
class ProdutosList(generics.ListAPIView): #generics.ListAPIView cria uma página que usa uma API que retorna todos os modelos para que possam ser visualizados.
    # queryset especifa quais dados serão pegos nessa API
    # (modelo.objects.all() pega todas os registro dessa tabela)
    queryset = ProdutoEletrInf.objects.all()
    # Especifica o serializador que converterá os dados para
    # que a API possa utilizar. (Dados -> JSON e JSON -> Dados)
    serializer_class = ProdutoEletrInfSerializer
    # Especifica qual classe será responsável por autenticar o
    # acesso a API.
    authentication_classes = [SessionAuthentication]
    # Especifica quem pode acessar essa API.
    # AllowAny  - Qualquer um.
    # IsAuthenticated - Somente quem estiver logado. (usuário
    # normal e admin)
    # IsAdminUser - Somente se estiver logado e for um admin
    # poderá acessar.
    permission_classes = (IsAuthenticated,)
    # Especifica a classe responsável por filtrar e organizar
    # os dados usados nessa API
    filter_backends = (filters.DjangoFilterBackend,)
    # Especifica quais dados serão passados (usados) nesse
    # filtro do Django.
    filter_fields = '__all__'

# Página responsável por editar, deletar e visualizar um registro
# especifico da tabela de produto.
class ProdutoDetail(generics.RetrieveUpdateDestroyAPIView): #generics.ListAPIView cria uma página que usa uma API que é capaz de pegar informações, deletar e editar um modelo especifico.
    queryset = ProdutoEletrInf.objects.all()
    serializer_class = ProdutoEletrInfSerializer
    authentication_classes = [SessionAuthentication]
    # Somente usuários admin podem editar, ou apagar um
    # produto especifico usando a API.
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = '__all__'

# Página responsável por listar todas as variações de preços
# referentes a um produto. (Preço, e Data-Hora daquele preço)
class ProdutoInfPrecos(generics.ListAPIView):
    # Não foi definido o queryset diretamente aqui, pois primeiro foi feito um tratamento com os dados do banco para ver quais serão inclúidos no queryset. Ou seja quais serão exibidos.
    serializer_class = PrecoInfSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = '__all__'

    # Sobrescreve o método responsável por pegar os dados
    # para serem exibidos. Para pegar parametrô da url,
    # e mostrar dados referentes a ele.
    def get_queryset(self):
        # Pega o id de um produto, e retorna todos os
        # preços referentes a ele
        # -----------------------------------------------

        # Pega o parâmetro da url, com nome de "pk"
        id_produto = self.kwargs["pk"]
        try:
            # Pega o modelo de produto com o id especificado
            produto_referencia = ProdutoEletrInf.objects.get(pk=id_produto)

            # Pega todas os modelos de precos que "apontam"
            # para esse Tênis que foi encontrado.
            lista_variacoes_precos = PrecoInf.objects.filter(produto_referencia=produto_referencia)
        # Senão existir um produto com aquele id ou se ele não tiver preços
        # ligado a ele, retorna status 404. (Não encontrado)
        except django_exceptions.ObjectDoesNotExist:
            raise Http404

        return lista_variacoes_precos

# Página responsável por listar todos os modelos de
# preços existentes
class PrecosList(generics.ListAPIView):
    queryset = PrecoInf.objects.all()
    serializer_class = PrecoInfSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = '__all__'

# Página responsável por pegar o "pai" dessa modelo
# de preço. (Ou seja o produto a quem esse preço se
# refe-re)
class PrecoInfPai(generics.ListAPIView):
    serializer_class = ProdutoEletrInfSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = '__all__'

    def get_queryset(self):
        # Pega o id de um preço, e retorna o produto
        # que esse preço se refe-re. (O pai)
        # -----------------------------------------------

        # Pega o valor do parâmetro passado a url que
        # tem o nome de pk
        try:
            id_preco = self.kwargs["pk"]
            preco_referencia = PrecoInf.objects.get(pk=id_preco)
            referecia_pai = preco_referencia.produto_referencia

            produto_pai = ProdutoEletrInf.objects.filter(pk=referecia_pai.pk)
        except django_exceptions.ObjectDoesNotExist:
            raise Http404

        return produto_pai
