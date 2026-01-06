"""
Capa de Datos - Modelos Django
==============================
Este módulo define los modelos de datos que representan las entidades
del sistema de trazabilidad de productos agrícolas.

Utiliza Django ORM para mapear estas clases a tablas en la base de datos SQLite.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class LoteCultivo(models.Model):
    """
    Modelo que representa el origen del producto (lote de cultivo).
    
    Almacena información sobre el lote donde se cultivó el producto,
    incluyendo datos del cultivo y fecha de cosecha.
    """
    # Campos del lote
    codigo_lote = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Lote",
        help_text="Identificador único del lote de cultivo"
    )
    tipo_producto = models.CharField(
        max_length=100,
        verbose_name="Tipo de Producto",
        default="Mango Orgánico",
        help_text="Tipo de producto agrícola (ej: Mango Orgánico)"
    )
    ubicacion = models.CharField(
        max_length=200,
        verbose_name="Ubicación",
        help_text="Ubicación geográfica del lote de cultivo"
    )
    area_hectareas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Área (hectáreas)",
        help_text="Área del lote en hectáreas"
    )
    
    # Fecha de cosecha
    fecha_cosecha = models.DateField(
        verbose_name="Fecha de Cosecha",
        help_text="Fecha en que se realizó la cosecha del lote"
    )
    
    # Información adicional
    responsable = models.CharField(
        max_length=100,
        verbose_name="Responsable",
        help_text="Nombre del responsable del lote"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Lote de Cultivo"
        verbose_name_plural = "Lotes de Cultivo"
        ordering = ['-fecha_cosecha', 'codigo_lote']
    
    def __str__(self):
        return f"{self.codigo_lote} - {self.tipo_producto} ({self.fecha_cosecha})"


class Transformacion(models.Model):
    """
    Modelo que representa el proceso de transformación del producto.
    
    Almacena información sobre lavado, empaquetado y controles de calidad
    realizados al producto después de la cosecha.
    """
    # Relación con el lote de cultivo
    lote = models.ForeignKey(
        LoteCultivo,
        on_delete=models.CASCADE,
        related_name='transformaciones',
        verbose_name="Lote de Cultivo",
        help_text="Lote de cultivo asociado a esta transformación"
    )
    
    # Datos de lavado
    fecha_lavado = models.DateTimeField(
        verbose_name="Fecha de Lavado",
        help_text="Fecha y hora en que se realizó el lavado"
    )
    temperatura_lavado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Temperatura de Lavado (°C)",
        help_text="Temperatura del agua utilizada en el lavado"
    )
    responsable_lavado = models.CharField(
        max_length=100,
        verbose_name="Responsable de Lavado"
    )
    
    # Datos de empaquetado
    fecha_empaquetado = models.DateTimeField(
        verbose_name="Fecha de Empaquetado",
        help_text="Fecha y hora en que se realizó el empaquetado"
    )
    tipo_empaque = models.CharField(
        max_length=100,
        verbose_name="Tipo de Empaque",
        help_text="Tipo de empaque utilizado (ej: Caja de cartón, Bolsa plástica)"
    )
    cantidad_unidades = models.PositiveIntegerField(
        verbose_name="Cantidad de Unidades",
        help_text="Número de unidades empacadas"
    )
    responsable_empaquetado = models.CharField(
        max_length=100,
        verbose_name="Responsable de Empaquetado"
    )
    
    # Controles de calidad
    fecha_control_calidad = models.DateTimeField(
        verbose_name="Fecha de Control de Calidad"
    )
    resultado_calidad = models.CharField(
        max_length=20,
        choices=[
            ('APROBADO', 'Aprobado'),
            ('RECHAZADO', 'Rechazado'),
            ('CONDICIONAL', 'Condicional')
        ],
        verbose_name="Resultado de Control de Calidad"
    )
    observaciones_calidad = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones de Calidad",
        help_text="Observaciones o comentarios sobre el control de calidad"
    )
    responsable_calidad = models.CharField(
        max_length=100,
        verbose_name="Responsable de Control de Calidad"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Transformación"
        verbose_name_plural = "Transformaciones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Transformación {self.lote.codigo_lote} - {self.resultado_calidad}"


class Logistica(models.Model):
    """
    Modelo que representa la información logística del transporte.
    
    Almacena datos sobre el transporte del producto, incluyendo
    registro de temperatura durante el transporte y fecha de entrega.
    """
    # Relación con la transformación
    transformacion = models.ForeignKey(
        Transformacion,
        on_delete=models.CASCADE,
        related_name='logisticas',
        verbose_name="Transformación",
        help_text="Transformación asociada a este registro logístico"
    )
    
    # Datos del transporte
    numero_guia = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de Guía",
        help_text="Número de guía de transporte"
    )
    vehiculo = models.CharField(
        max_length=100,
        verbose_name="Vehículo",
        help_text="Identificación del vehículo de transporte"
    )
    conductor = models.CharField(
        max_length=100,
        verbose_name="Conductor",
        help_text="Nombre del conductor"
    )
    
    # Registro de temperatura
    temperatura_minima = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Temperatura Mínima (°C)",
        help_text="Temperatura mínima registrada durante el transporte"
    )
    temperatura_maxima = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Temperatura Máxima (°C)",
        help_text="Temperatura máxima registrada durante el transporte"
    )
    temperatura_promedio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Temperatura Promedio (°C)",
        help_text="Temperatura promedio durante el transporte"
    )
    
    # Fechas de transporte
    fecha_salida = models.DateTimeField(
        verbose_name="Fecha de Salida",
        help_text="Fecha y hora de salida del almacén"
    )
    fecha_entrega = models.DateTimeField(
        verbose_name="Fecha de Entrega",
        help_text="Fecha y hora de entrega al supermercado"
    )
    
    # Destino
    destino = models.CharField(
        max_length=200,
        verbose_name="Destino",
        help_text="Nombre del supermercado o punto de entrega"
    )
    direccion_destino = models.TextField(
        verbose_name="Dirección de Destino",
        help_text="Dirección completa del destino"
    )
    
    # Estado del transporte
    estado = models.CharField(
        max_length=20,
        choices=[
            ('EN_TRANSITO', 'En Tránsito'),
            ('ENTREGADO', 'Entregado'),
            ('RETRASADO', 'Retrasado')
        ],
        default='EN_TRANSITO',
        verbose_name="Estado"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Logística"
        verbose_name_plural = "Logísticas"
        ordering = ['-fecha_entrega']
    
    def __str__(self):
        return f"Logística {self.numero_guia} - {self.destino}"
