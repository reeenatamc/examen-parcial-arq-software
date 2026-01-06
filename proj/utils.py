"""
Utilidades para el sistema de trazabilidad.
Contiene funciones auxiliares para auditoría y otros propósitos.
"""

from .models import Auditoria
from django.utils import timezone


def registrar_auditoria(tipo_entidad, entidad_id, accion, descripcion, 
                       campo_modificado=None, valor_anterior=None, 
                       valor_nuevo=None, usuario=None, request=None):
    """
    Registra un cambio en el sistema de auditoría.
    
    Args:
        tipo_entidad: Tipo de entidad (Auditoria.TIPO_LOTE, etc.)
        entidad_id: ID de la entidad modificada
        accion: Acción realizada (Auditoria.ACCION_CREAR, etc.)
        descripcion: Descripción del cambio
        campo_modificado: Campo que fue modificado (opcional)
        valor_anterior: Valor anterior del campo (opcional)
        valor_nuevo: Valor nuevo del campo (opcional)
        usuario: Usuario que realizó el cambio (opcional)
        request: Objeto request de Django para obtener IP (opcional)
    """
    ip_address = None
    if request:
        # Obtener la IP del cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    Auditoria.objects.create(
        tipo_entidad=tipo_entidad,
        entidad_id=entidad_id,
        accion=accion,
        campo_modificado=campo_modificado,
        valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
        valor_nuevo=str(valor_nuevo) if valor_nuevo is not None else None,
        descripcion=descripcion,
        usuario=usuario,
        ip_address=ip_address
    )

