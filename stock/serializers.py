from rest_framework import serializers
from .models import Producto, Lote, MovimientoStock

class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = ('id','numero_lote','fecha_venc','stock','producto')

class ProductoSerializer(serializers.ModelSerializer):
    lotes = LoteSerializer(many=True, read_only=True)
    class Meta:
        model = Producto
        fields = ('id','gtin','nombre','laboratorio','estado','lotes')

class MovimientoStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoStock
        fields = ('id','lote','tipo','cantidad','motivo','documento_ref','creado_en')

    def create(self, validated_data):
        mov = MovimientoStock(**validated_data)
        mov.save()         # crea el registro
        mov.aplicar()      # aplica al stock (transacción)
        return mov
