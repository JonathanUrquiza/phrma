from django.contrib import admin
from .models import Producto, Lote, MovimientoStock

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id','gtin','nombre','laboratorio','estado','actualizado_en')
    search_fields = ('gtin','nombre','laboratorio')
    list_filter = ('estado',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('id','producto','numero_lote','fecha_venc','stock')
    list_filter = ('fecha_venc',)
    search_fields = ('numero_lote','producto__nombre','producto__gtin')

@admin.register(MovimientoStock)
class MovAdmin(admin.ModelAdmin):
    list_display = ('id','lote','tipo','cantidad','documento_ref','creado_en')
    list_filter = ('tipo',)
    search_fields = ('lote__numero_lote','lote__producto__gtin','documento_ref')
