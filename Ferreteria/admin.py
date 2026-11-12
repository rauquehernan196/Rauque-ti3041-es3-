from django.contrib import admin

from .models import ConsultaCliente, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'archivado')
    list_editable = ('archivado',)
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'archivado')


@admin.register(ConsultaCliente)
class ConsultaClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'producto_interes', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('nombre', 'correo', 'mensaje', 'producto_interes__nombre')
    date_hierarchy = 'fecha'
    list_select_related = ('producto_interes',)