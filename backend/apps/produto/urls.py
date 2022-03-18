from django.urls import re_path
from . import views

# -------------------------------------------------------------------------
# Configura todas os caminhos de urls que estão disponíveis para o app
# django "produto".
# (As urls por vês são ligadas a views que são APIs ou sites que podem ser
# acessados.
# -------------------------------------------------------------------------

urlpatterns = [
    re_path(r'^ListaProdutos/', views.ProdutosList().as_view(), name='produto-lista'),
    re_path(r'^DetalhesProduto/(?P<pk>[0-9]+)/$', views.ProdutoDetail().as_view(), name='produto-detalhe'),
    re_path(r'^Produto/(?P<pk>[0-9]+)/HistPrecos', views.ProdutoInfPrecos().as_view(), name='produto-hist-precos'),

    re_path(r'^ListaPrecos/', views.PrecosList().as_view(), name='preco-lista'),
    re_path(r'^Preco/(?P<pk>[0-9]+)/ProdutoPai', views.PrecoInfPai().as_view(), name='preco-produto-pai')
]
