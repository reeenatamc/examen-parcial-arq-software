"""
URLs de la aplicación proj (Trazabilidad)
"""
from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.index, name='index'),
    
    # URLs para Lotes de Cultivo (Origen)
    path('lotes/', views.lista_lotes, name='lista_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/<int:pk>/', views.detalle_lote, name='detalle_lote'),
    path('lotes/<int:lote_pk>/trazabilidad/', views.trazabilidad_completa, name='trazabilidad_completa'),
    
    # URLs para Transformaciones
    path('transformaciones/', views.lista_transformaciones, name='lista_transformaciones'),
    path('transformaciones/crear/', views.crear_transformacion, name='crear_transformacion'),
    
    # URLs para Logísticas
    path('logisticas/', views.lista_logisticas, name='lista_logisticas'),
    path('logisticas/crear/', views.crear_logistica, name='crear_logistica'),
    path('logisticas/<int:pk>/editar/', views.editar_logistica, name='editar_logistica'),
    
    # URLs para Trazabilidades
    path('trazabilidades/', views.lista_trazabilidades, name='lista_trazabilidades'),
    path('buscar/', views.buscar_por_codigo, name='buscar_trazabilidad'),
]

