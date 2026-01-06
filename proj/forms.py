"""
Capa de Presentación - Formularios Django
==========================================
Este módulo define los formularios utilizados en la interfaz de usuario
para capturar datos de trazabilidad del usuario.

Los formularios se conectan con la capa de lógica de negocio para
aplicar las validaciones antes de guardar en la base de datos.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import LoteCultivo, Transformacion, Logistica
from .business_logic.validaciones import (
    ValidadorLoteCultivo,
    ValidadorTransformacion,
    ValidadorLogistica,
    ValidacionTrazabilidadError
)


class LoteCultivoForm(forms.ModelForm):
    """
    Formulario para capturar datos del Lote de Cultivo (Origen).
    
    Permite al usuario ingresar información sobre el lote de cultivo
    y fecha de cosecha.
    """
    
    class Meta:
        model = LoteCultivo
        fields = [
            'codigo_lote',
            'tipo_producto',
            'ubicacion',
            'latitud',
            'longitud',
            'area_hectareas',
            'fecha_cosecha',
            'responsable',
            'es_organico',
            'certificaciones'
        ]
        widgets = {
            'codigo_lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LOTE-2024-001'
            }),
            'tipo_producto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mango Orgánico'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Finca San José, Valle Central'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Ej: 9.928069'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Ej: -84.090725'
            }),
            'area_hectareas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'fecha_cosecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable'
            }),
            'es_organico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ej: Certificado Orgánico USDA, Fair Trade, GlobalGAP'
            })
        }
        labels = {
            'codigo_lote': 'Código del Lote *',
            'tipo_producto': 'Tipo de Producto *',
            'ubicacion': 'Ubicación *',
            'latitud': 'Latitud GPS',
            'longitud': 'Longitud GPS',
            'area_hectareas': 'Área (hectáreas) *',
            'fecha_cosecha': 'Fecha de Cosecha *',
            'responsable': 'Responsable *',
            'es_organico': 'Producto Orgánico',
            'certificaciones': 'Certificaciones'
        }
    
    def clean_codigo_lote(self):
        """Valida el código de lote usando la capa de lógica de negocio."""
        codigo = self.cleaned_data.get('codigo_lote')
        try:
            ValidadorLoteCultivo.validar_codigo_lote(codigo)
        except ValidacionTrazabilidadError as e:
            raise ValidationError(str(e))
        return codigo
    
    def clean_fecha_cosecha(self):
        """Valida la fecha de cosecha usando la capa de lógica de negocio."""
        fecha = self.cleaned_data.get('fecha_cosecha')
        if fecha:
            try:
                ValidadorLoteCultivo.validar_fecha_cosecha(fecha)
            except ValidacionTrazabilidadError as e:
                raise ValidationError(str(e))
        return fecha


class TransformacionForm(forms.ModelForm):
    """
    Formulario para capturar datos del proceso de Transformación.
    
    Permite ingresar información sobre lavado, empaquetado y
    controles de calidad.
    """
    
    class Meta:
        model = Transformacion
        fields = [
            'lote',
            'fecha_lavado',
            'temperatura_lavado',
            'responsable_lavado',
            'fecha_empaquetado',
            'tipo_empaque',
            'cantidad_unidades',
            'responsable_empaquetado',
            'fecha_control_calidad',
            'resultado_calidad',
            'observaciones_calidad',
            'responsable_calidad'
        ]
        widgets = {
            'lote': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_lavado': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'temperatura_lavado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Entre 10°C y 40°C'
            }),
            'responsable_lavado': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fecha_empaquetado': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo_empaque': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Caja de cartón, Bolsa plástica'
            }),
            'cantidad_unidades': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'responsable_empaquetado': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fecha_control_calidad': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'resultado_calidad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observaciones_calidad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'responsable_calidad': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'lote': 'Lote de Cultivo *',
            'fecha_lavado': 'Fecha y Hora de Lavado *',
            'temperatura_lavado': 'Temperatura de Lavado (°C) *',
            'responsable_lavado': 'Responsable de Lavado *',
            'fecha_empaquetado': 'Fecha y Hora de Empaquetado *',
            'tipo_empaque': 'Tipo de Empaque *',
            'cantidad_unidades': 'Cantidad de Unidades *',
            'responsable_empaquetado': 'Responsable de Empaquetado *',
            'fecha_control_calidad': 'Fecha y Hora de Control de Calidad *',
            'resultado_calidad': 'Resultado de Control de Calidad *',
            'observaciones_calidad': 'Observaciones',
            'responsable_calidad': 'Responsable de Control de Calidad *'
        }
    
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con los lotes disponibles."""
        super().__init__(*args, **kwargs)
        # Solo mostrar lotes que no tengan transformación asociada
        self.fields['lote'].queryset = LoteCultivo.objects.all()
        self.fields['lote'].empty_label = "Seleccione un lote"
    
    def clean_temperatura_lavado(self):
        """Valida la temperatura de lavado usando la capa de lógica de negocio."""
        temperatura = self.cleaned_data.get('temperatura_lavado')
        if temperatura is not None:
            try:
                ValidadorTransformacion.validar_temperatura_lavado(temperatura)
            except ValidacionTrazabilidadError as e:
                raise ValidationError(str(e))
        return temperatura
    
    def clean_cantidad_unidades(self):
        """Valida la cantidad de unidades usando la capa de lógica de negocio."""
        cantidad = self.cleaned_data.get('cantidad_unidades')
        if cantidad is not None:
            try:
                ValidadorTransformacion.validar_cantidad_unidades(cantidad)
            except ValidacionTrazabilidadError as e:
                raise ValidationError(str(e))
        return cantidad
    
    def clean(self):
        """Valida la secuencia de fechas usando la capa de lógica de negocio."""
        cleaned_data = super().clean()
        fecha_lavado = cleaned_data.get('fecha_lavado')
        fecha_empaquetado = cleaned_data.get('fecha_empaquetado')
        fecha_control = cleaned_data.get('fecha_control_calidad')
        
        if fecha_lavado and fecha_empaquetado and fecha_control:
            try:
                ValidadorTransformacion.validar_secuencia_fechas(
                    fecha_lavado,
                    fecha_empaquetado,
                    fecha_control
                )
            except ValidacionTrazabilidadError as e:
                raise ValidationError({
                    'fecha_control_calidad': str(e)
                })
        
        return cleaned_data


class LogisticaForm(forms.ModelForm):
    """
    Formulario para capturar datos de Logística (Transporte).
    
    Permite ingresar información sobre el transporte, incluyendo
    registro de temperatura y fecha de entrega.
    """
    
    class Meta:
        model = Logistica
        fields = [
            'transformacion',
            'numero_guia',
            'vehiculo',
            'conductor',
            'temperatura_minima',
            'temperatura_maxima',
            'temperatura_promedio',
            'fecha_salida',
            'fecha_entrega',
            'destino',
            'direccion_destino',
            'estado',
            'distancia_km',
            'observaciones_transporte'
        ]
        widgets = {
            'transformacion': forms.Select(attrs={
                'class': 'form-control'
            }),
            'numero_guia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: GUI-2024-001'
            }),
            'vehiculo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Placa ABC-123'
            }),
            'conductor': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'temperatura_minima': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Mín: 2°C'
            }),
            'temperatura_maxima': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Máx: 8°C'
            }),
            'temperatura_promedio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Entre 2°C y 8°C'
            }),
            'fecha_salida': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_entrega': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Supermercado Central'
            }),
            'direccion_destino': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'distancia_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ej: 150.50'
            }),
            'observaciones_transporte': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales sobre el transporte'
            })
        }
        labels = {
            'transformacion': 'Transformación *',
            'numero_guia': 'Número de Guía *',
            'vehiculo': 'Vehículo *',
            'conductor': 'Conductor *',
            'temperatura_minima': 'Temperatura Mínima (°C) *',
            'temperatura_maxima': 'Temperatura Máxima (°C) *',
            'temperatura_promedio': 'Temperatura Promedio (°C) *',
            'fecha_salida': 'Fecha y Hora de Salida *',
            'fecha_entrega': 'Fecha y Hora de Entrega *',
            'destino': 'Destino (Supermercado) *',
            'direccion_destino': 'Dirección de Destino *',
            'estado': 'Estado *',
            'distancia_km': 'Distancia (km)',
            'observaciones_transporte': 'Observaciones del Transporte'
        }
    
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con las transformaciones disponibles."""
        super().__init__(*args, **kwargs)
        # Solo mostrar transformaciones que no tengan logística asociada
        self.fields['transformacion'].queryset = Transformacion.objects.all()
        self.fields['transformacion'].empty_label = "Seleccione una transformación"
    
    def clean_numero_guia(self):
        """Valida el número de guía usando la capa de lógica de negocio."""
        numero = self.cleaned_data.get('numero_guia')
        if numero:
            try:
                ValidadorLogistica.validar_numero_guia(numero)
            except ValidacionTrazabilidadError as e:
                raise ValidationError(str(e))
        return numero
    
    def clean(self):
        """Valida las temperaturas y fechas usando la capa de lógica de negocio."""
        cleaned_data = super().clean()
        
        temp_min = cleaned_data.get('temperatura_minima')
        temp_max = cleaned_data.get('temperatura_maxima')
        temp_prom = cleaned_data.get('temperatura_promedio')
        fecha_salida = cleaned_data.get('fecha_salida')
        fecha_entrega = cleaned_data.get('fecha_entrega')
        
        # Validar temperaturas
        if temp_min is not None and temp_max is not None and temp_prom is not None:
            try:
                ValidadorLogistica.validar_temperaturas_transporte(
                    temp_min,
                    temp_max,
                    temp_prom
                )
            except ValidacionTrazabilidadError as e:
                raise ValidationError({
                    'temperatura_promedio': str(e)
                })
        
        # Validar fechas
        if fecha_salida and fecha_entrega:
            try:
                ValidadorLogistica.validar_fechas_transporte(
                    fecha_salida,
                    fecha_entrega
                )
            except ValidacionTrazabilidadError as e:
                raise ValidationError({
                    'fecha_entrega': str(e)
                })
        
        return cleaned_data

