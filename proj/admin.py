"""
Registro de modelos en el admin de Django.
Permite gestionar los datos desde la interfaz administrativa.
"""

from django.contrib import admin
from .models import LoteCultivo, Transformacion, Logistica, Auditoria


@admin.register(LoteCultivo)
class LoteCultivoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo LoteCultivo.
    """
    list_display = [
        'codigo_lote',
        'tipo_producto',
        'ubicacion',
        'es_organico',
        'fecha_cosecha',
        'responsable',
        'fecha_creacion'
    ]
    list_filter = ['fecha_cosecha', 'tipo_producto', 'fecha_creacion']
    search_fields = ['codigo_lote', 'tipo_producto', 'ubicacion', 'responsable']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_cosecha'


@admin.register(Transformacion)
class TransformacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Transformacion.
    """
    list_display = [
        'lote',
        'fecha_lavado',
        'fecha_empaquetado',
        'resultado_calidad',
        'cantidad_unidades',
        'fecha_creacion'
    ]
    list_filter = ['resultado_calidad', 'fecha_creacion', 'fecha_lavado']
    search_fields = [
        'lote__codigo_lote',
        'responsable_lavado',
        'responsable_empaquetado',
        'responsable_calidad'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_creacion'


@admin.register(Logistica)
class LogisticaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Logistica.
    """
    list_display = [
        'numero_guia',
        'codigo_trazabilidad',
        'transformacion',
        'destino',
        'fecha_salida',
        'fecha_entrega',
        'temperatura_promedio',
        'estado'
    ]
    list_filter = ['estado', 'fecha_salida', 'fecha_entrega']
    search_fields = [
        'numero_guia',
        'vehiculo',
        'conductor',
        'destino',
        'transformacion__lote__codigo_lote'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_salida'


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Auditoria.
    """
    list_display = [
        'fecha_cambio',
        'tipo_entidad',
        'entidad_id',
        'accion',
        'campo_modificado',
        'descripcion',
        'usuario',
        'ip_address'
    ]
    list_filter = ['tipo_entidad', 'accion', 'fecha_cambio']
    search_fields = [
        'descripcion',
        'usuario',
        'ip_address',
        'campo_modificado'
    ]
    readonly_fields = ['fecha_cambio']
    date_hierarchy = 'fecha_cambio'
