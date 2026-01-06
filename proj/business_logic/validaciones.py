"""
Capa de Lógica de Negocio - Validaciones
=========================================
Este módulo contiene todas las reglas de negocio y validaciones
para el sistema de trazabilidad de productos agrícolas.

Las validaciones aseguran la integridad de los datos y el cumplimiento
de los estándares de calidad y seguridad alimentaria.
"""

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone


class ValidacionTrazabilidadError(Exception):
    """Excepción personalizada para errores de validación de trazabilidad."""
    pass


class ValidadorLoteCultivo:
    """
    Validador para la capa de negocio de Lote de Cultivo.
    
    Contiene las reglas de negocio para validar los datos de origen
    del producto (lote de cultivo).
    """
    
    @staticmethod
    def validar_fecha_cosecha(fecha_cosecha):
        """
        Valida que la fecha de cosecha no sea en el futuro.
        
        Args:
            fecha_cosecha: Objeto date con la fecha de cosecha
            
        Raises:
            ValidacionTrazabilidadError: Si la fecha es inválida
        """
        if fecha_cosecha > timezone.now().date():
            raise ValidacionTrazabilidadError(
                "La fecha de cosecha no puede ser en el futuro."
            )
    
    @staticmethod
    def validar_codigo_lote(codigo_lote):
        """
        Valida el formato del código de lote.
        
        El código debe tener al menos 3 caracteres y comenzar con letras.
        
        Args:
            codigo_lote: String con el código del lote
            
        Raises:
            ValidacionTrazabilidadError: Si el código es inválido
        """
        if not codigo_lote:
            raise ValidacionTrazabilidadError(
                "El código de lote es obligatorio."
            )
        
        if len(codigo_lote) < 3:
            raise ValidacionTrazabilidadError(
                "El código de lote debe tener al menos 3 caracteres."
            )
        
        if not codigo_lote[0].isalpha():
            raise ValidacionTrazabilidadError(
                "El código de lote debe comenzar con una letra."
            )


class ValidadorTransformacion:
    """
    Validador para la capa de negocio de Transformación.
    
    Contiene las reglas de negocio para validar los procesos
    de transformación (lavado, empaquetado, control de calidad).
    """
    
    # Rangos de temperatura permitidos (en grados Celsius)
    TEMP_MIN_LAVADO = 10.0
    TEMP_MAX_LAVADO = 40.0
    
    @staticmethod
    def validar_temperatura_lavado(temperatura):
        """
        Valida que la temperatura de lavado esté dentro del rango permitido.
        
        La temperatura debe estar entre 10°C y 40°C para garantizar
        la calidad del producto sin dañarlo.
        
        Args:
            temperatura: Decimal con la temperatura en grados Celsius
            
        Raises:
            ValidacionTrazabilidadError: Si la temperatura está fuera del rango
        """
        if temperatura < ValidadorTransformacion.TEMP_MIN_LAVADO:
            raise ValidacionTrazabilidadError(
                f"La temperatura de lavado ({temperatura}°C) está por debajo "
                f"del mínimo permitido ({ValidadorTransformacion.TEMP_MIN_LAVADO}°C)."
            )
        
        if temperatura > ValidadorTransformacion.TEMP_MAX_LAVADO:
            raise ValidacionTrazabilidadError(
                f"La temperatura de lavado ({temperatura}°C) está por encima "
                f"del máximo permitido ({ValidadorTransformacion.TEMP_MAX_LAVADO}°C)."
            )
    
    @staticmethod
    def validar_secuencia_fechas(fecha_lavado, fecha_empaquetado, fecha_control):
        """
        Valida que las fechas de los procesos estén en el orden correcto.
        
        El orden debe ser: Lavado -> Empaquetado -> Control de Calidad
        
        Args:
            fecha_lavado: DateTime del lavado
            fecha_empaquetado: DateTime del empaquetado
            fecha_control: DateTime del control de calidad
            
        Raises:
            ValidacionTrazabilidadError: Si las fechas están en orden incorrecto
        """
        if fecha_empaquetado < fecha_lavado:
            raise ValidacionTrazabilidadError(
                "El empaquetado no puede ocurrir antes del lavado."
            )
        
        if fecha_control < fecha_empaquetado:
            raise ValidacionTrazabilidadError(
                "El control de calidad no puede ocurrir antes del empaquetado."
            )
    
    @staticmethod
    def validar_cantidad_unidades(cantidad):
        """
        Valida que la cantidad de unidades sea válida.
        
        Args:
            cantidad: Entero positivo con la cantidad de unidades
            
        Raises:
            ValidacionTrazabilidadError: Si la cantidad es inválida
        """
        if cantidad <= 0:
            raise ValidacionTrazabilidadError(
                "La cantidad de unidades debe ser mayor a cero."
            )
        
        if cantidad > 100000:
            raise ValidacionTrazabilidadError(
                "La cantidad de unidades no puede exceder 100,000."
            )


class ValidadorLogistica:
    """
    Validador para la capa de negocio de Logística.
    
    Contiene las reglas de negocio para validar los datos de transporte
    y logística, especialmente las temperaturas durante el transporte.
    """
    
    # Rangos de temperatura permitidos durante el transporte (en grados Celsius)
    TEMP_MIN_TRANSPORTE = 2.0
    TEMP_MAX_TRANSPORTE = 8.0
    
    @staticmethod
    def validar_temperaturas_transporte(temp_min, temp_max, temp_promedio):
        """
        Valida que las temperaturas de transporte estén dentro del rango permitido.
        
        Para productos orgánicos como mangos, la temperatura debe mantenerse
        entre 2°C y 8°C durante el transporte para preservar la calidad.
        
        Args:
            temp_min: Temperatura mínima registrada
            temp_max: Temperatura máxima registrada
            temp_promedio: Temperatura promedio
            
        Raises:
            ValidacionTrazabilidadError: Si alguna temperatura está fuera del rango
        """
        # Validar temperatura mínima
        if temp_min < ValidadorLogistica.TEMP_MIN_TRANSPORTE:
            raise ValidacionTrazabilidadError(
                f"La temperatura mínima ({temp_min}°C) está por debajo "
                f"del mínimo permitido ({ValidadorLogistica.TEMP_MIN_TRANSPORTE}°C). "
                "El producto puede haberse deteriorado."
            )
        
        # Validar temperatura máxima
        if temp_max > ValidadorLogistica.TEMP_MAX_TRANSPORTE:
            raise ValidacionTrazabilidadError(
                f"La temperatura máxima ({temp_max}°C) está por encima "
                f"del máximo permitido ({ValidadorLogistica.TEMP_MAX_TRANSPORTE}°C). "
                "El producto puede haberse deteriorado."
            )
        
        # Validar temperatura promedio
        if temp_promedio < ValidadorLogistica.TEMP_MIN_TRANSPORTE:
            raise ValidacionTrazabilidadError(
                f"La temperatura promedio ({temp_promedio}°C) está por debajo "
                f"del mínimo permitido ({ValidadorLogistica.TEMP_MIN_TRANSPORTE}°C)."
            )
        
        if temp_promedio > ValidadorLogistica.TEMP_MAX_TRANSPORTE:
            raise ValidacionTrazabilidadError(
                f"La temperatura promedio ({temp_promedio}°C) está por encima "
                f"del máximo permitido ({ValidadorLogistica.TEMP_MAX_TRANSPORTE}°C)."
            )
        
        # Validar coherencia de las temperaturas
        if temp_min > temp_max:
            raise ValidacionTrazabilidadError(
                "La temperatura mínima no puede ser mayor que la máxima."
            )
        
        if temp_promedio < temp_min or temp_promedio > temp_max:
            raise ValidacionTrazabilidadError(
                "La temperatura promedio debe estar entre la mínima y la máxima."
            )
    
    @staticmethod
    def validar_fechas_transporte(fecha_salida, fecha_entrega):
        """
        Valida que las fechas de transporte sean coherentes.
        
        La fecha de entrega debe ser posterior a la fecha de salida,
        y el tiempo de transporte no debe exceder las 72 horas.
        
        Args:
            fecha_salida: DateTime de salida
            fecha_entrega: DateTime de entrega
            
        Raises:
            ValidacionTrazabilidadError: Si las fechas son inválidas
        """
        if fecha_entrega < fecha_salida:
            raise ValidacionTrazabilidadError(
                "La fecha de entrega no puede ser anterior a la fecha de salida."
            )
        
        tiempo_transporte = fecha_entrega - fecha_salida
        
        if tiempo_transporte > timedelta(hours=72):
            raise ValidacionTrazabilidadError(
                "El tiempo de transporte no puede exceder las 72 horas."
            )
        
        if tiempo_transporte < timedelta(minutes=1):
            raise ValidacionTrazabilidadError(
                "El tiempo de transporte debe ser de al menos 1 minuto."
            )
    
    @staticmethod
    def validar_numero_guia(numero_guia):
        """
        Valida el formato del número de guía.
        
        Args:
            numero_guia: String con el número de guía
            
        Raises:
            ValidacionTrazabilidadError: Si el número de guía es inválido
        """
        if not numero_guia:
            raise ValidacionTrazabilidadError(
                "El número de guía es obligatorio."
            )
        
        if len(numero_guia) < 5:
            raise ValidacionTrazabilidadError(
                "El número de guía debe tener al menos 5 caracteres."
            )


class ServicioTrazabilidad:
    """
    Servicio principal de trazabilidad.
    
    Coordina las validaciones y operaciones de negocio
    relacionadas con la trazabilidad completa del producto.
    """
    
    @staticmethod
    def validar_trazabilidad_completa(lote, transformacion, logistica):
        """
        Valida que la cadena completa de trazabilidad sea coherente.
        
        Verifica que las relaciones entre lote, transformación y logística
        sean correctas y que los tiempos estén en orden lógico.
        
        Args:
            lote: Instancia de LoteCultivo
            transformacion: Instancia de Transformacion
            logistica: Instancia de Logistica
            
        Raises:
            ValidacionTrazabilidadError: Si la trazabilidad no es válida
        """
        # Validar que la transformación pertenece al lote
        if transformacion.lote_id != lote.id:
            raise ValidacionTrazabilidadError(
                "La transformación no corresponde al lote especificado."
            )
        
        # Validar que la logística pertenece a la transformación
        if logistica.transformacion_id != transformacion.id:
            raise ValidacionTrazabilidadError(
                "La logística no corresponde a la transformación especificada."
            )
        
        # Validar secuencia temporal
        # Cosecha -> Lavado -> Empaquetado -> Control -> Transporte -> Entrega
        if transformacion.fecha_lavado.date() < lote.fecha_cosecha:
            raise ValidacionTrazabilidadError(
                "El lavado no puede ocurrir antes de la cosecha."
            )
        
        if logistica.fecha_salida < transformacion.fecha_control_calidad:
            raise ValidacionTrazabilidadError(
                "El transporte no puede iniciar antes del control de calidad."
            )

