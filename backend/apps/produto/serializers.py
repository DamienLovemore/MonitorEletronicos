from rest_framework import serializers
from .models import ProdutoEletrInf, PrecoInf

# ----------------------------------------------------------------
# Serializers são reponsáveis por fazer a ligação dos dados entre
# o banco com a API REST. Eles pegam os dados e os transforma em
# JSON para poder exibir e utiliza-los, e depois das mudanças
# converte os dados de volta para passar pro banco.
# ----------------------------------------------------------------


class ProdutoEletrInfSerializer(serializers.ModelSerializer):
    class Meta:
        # Especifica a qual modelo esse serializer pertence
        model = ProdutoEletrInf
        # Especifica quais campos (todos) serão "serializados"
        # para poder serem usados na API REST.
        fields = '__all__'


class PrecoInfSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecoInf
        fields = '__all__'
