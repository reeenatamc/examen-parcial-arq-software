"""
Capa de Presentación - Vistas Django
=====================================
Este módulo contiene las vistas que manejan las peticiones HTTP
y coordinan la interacción entre la presentación (templates) y
la lógica de negocio.

Las vistas utilizan los formularios y servicios de la capa de negocio
para procesar y validar los datos antes de guardarlos.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .models import LoteCultivo, Transformacion, Logistica
from .forms import LoteCultivoForm, TransformacionForm, LogisticaForm
from .business_logic.validaciones import ServicioTrazabilidad, ValidacionTrazabilidadError


def index(request):
    """
    Vista principal que muestra el dashboard del sistema de trazabilidad.
    
    Muestra un resumen de la información de trazabilidad y enlaces
    a las diferentes secciones del sistema.
    """
    # Estadísticas para el dashboard
    total_lotes = LoteCultivo.objects.count()
    total_transformaciones = Transformacion.objects.count()
    total_logisticas = Logistica.objects.count()
    
    # Lotes recientes
    lotes_recientes = LoteCultivo.objects.all()[:5]
    
    # Transformaciones recientes
    transformaciones_recientes = Transformacion.objects.all()[:5]
    
    # Logísticas recientes
    logisticas_recientes = Logistica.objects.all()[:5]
    
    context = {
        'total_lotes': total_lotes,
        'total_transformaciones': total_transformaciones,
        'total_logisticas': total_logisticas,
        'lotes_recientes': lotes_recientes,
        'transformaciones_recientes': transformaciones_recientes,
        'logisticas_recientes': logisticas_recientes,
    }
    
    return render(request, 'proj/index.html', context)


def crear_lote(request):
    """
    Vista para crear un nuevo lote de cultivo.
    
    Maneja tanto GET (mostrar formulario) como POST (procesar datos).
    Utiliza la capa de lógica de negocio para validar los datos.
    """
    if request.method == 'POST':
        form = LoteCultivoForm(request.POST)
        if form.is_valid():
            # Los formularios ya aplican validaciones de la capa de negocio
            lote = form.save()
            messages.success(
                request,
                f'Lote de cultivo "{lote.codigo_lote}" creado exitosamente.'
            )
            return redirect('lista_lotes')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LoteCultivoForm()
    
    return render(request, 'proj/lote_form.html', {
        'form': form,
        'titulo': 'Nuevo Lote de Cultivo',
        'accion': 'Crear'
    })


def lista_lotes(request):
    """
    Vista que lista todos los lotes de cultivo registrados.
    """
    lotes = LoteCultivo.objects.all()
    return render(request, 'proj/lista_lotes.html', {'lotes': lotes})


def detalle_lote(request, pk):
    """
    Vista que muestra los detalles completos de un lote de cultivo.
    
    Incluye información sobre transformaciones y logística asociadas.
    """
    lote = get_object_or_404(LoteCultivo, pk=pk)
    transformaciones = lote.transformaciones.all()
    
    # Obtener logísticas relacionadas a través de transformaciones
    logisticas = Logistica.objects.filter(transformacion__lote=lote)
    
    return render(request, 'proj/detalle_lote.html', {
        'lote': lote,
        'transformaciones': transformaciones,
        'logisticas': logisticas
    })


def crear_transformacion(request):
    """
    Vista para crear un nuevo registro de transformación.
    
    Maneja tanto GET (mostrar formulario) como POST (procesar datos).
    Utiliza la capa de lógica de negocio para validar los datos.
    """
    if request.method == 'POST':
        form = TransformacionForm(request.POST)
        if form.is_valid():
            # Los formularios ya aplican validaciones de la capa de negocio
            transformacion = form.save()
            messages.success(
                request,
                f'Transformación para el lote "{transformacion.lote.codigo_lote}" creada exitosamente.'
            )
            return redirect('lista_transformaciones')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = TransformacionForm()
    
    return render(request, 'proj/transformacion_form.html', {
        'form': form,
        'titulo': 'Nueva Transformación',
        'accion': 'Crear'
    })


def lista_transformaciones(request):
    """
    Vista que lista todas las transformaciones registradas.
    """
    transformaciones = Transformacion.objects.select_related('lote').all()
    return render(request, 'proj/lista_transformaciones.html', {
        'transformaciones': transformaciones
    })


def crear_logistica(request):
    """
    Vista para crear un nuevo registro de logística.
    
    Maneja tanto GET (mostrar formulario) como POST (procesar datos).
    Utiliza la capa de lógica de negocio para validar los datos.
    """
    if request.method == 'POST':
        form = LogisticaForm(request.POST)
        if form.is_valid():
            # Validar trazabilidad completa
            try:
                transformacion = form.cleaned_data['transformacion']
                lote = transformacion.lote
                logistica = form.save(commit=False)
                
                # Validar trazabilidad completa usando servicio de negocio
                ServicioTrazabilidad.validar_trazabilidad_completa(
                    lote,
                    transformacion,
                    logistica
                )
                
                logistica.save()
                messages.success(
                    request,
                    f'Registro logístico "{logistica.numero_guia}" creado exitosamente.'
                )
                return redirect('lista_logisticas')
            except ValidacionTrazabilidadError as e:
                messages.error(request, f'Error de validación: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LogisticaForm()
    
    return render(request, 'proj/logistica_form.html', {
        'form': form,
        'titulo': 'Nueva Logística',
        'accion': 'Crear'
    })


def lista_logisticas(request):
    """
    Vista que lista todos los registros logísticos.
    """
    logisticas = Logistica.objects.select_related(
        'transformacion__lote'
    ).all()
    return render(request, 'proj/lista_logisticas.html', {
        'logisticas': logisticas
    })


def trazabilidad_completa(request, lote_pk):
    """
    Vista que muestra la trazabilidad completa de un producto.
    
    Muestra el flujo completo: Lote -> Transformación -> Logística
    """
    lote = get_object_or_404(LoteCultivo, pk=lote_pk)
    transformaciones = lote.transformaciones.all()
    
    # Obtener todas las logísticas relacionadas
    logisticas = Logistica.objects.filter(transformacion__lote=lote)
    
    # Validar trazabilidad completa
    errores_validacion = []
    if transformaciones.exists() and logisticas.exists():
        for transformacion in transformaciones:
            for logistica in logisticas.filter(transformacion=transformacion):
                try:
                    ServicioTrazabilidad.validar_trazabilidad_completa(
                        lote,
                        transformacion,
                        logistica
                    )
                except ValidacionTrazabilidadError as e:
                    errores_validacion.append(str(e))
    
    return render(request, 'proj/trazabilidad_completa.html', {
        'lote': lote,
        'transformaciones': transformaciones,
        'logisticas': logisticas,
        'errores_validacion': errores_validacion
    })


def lista_trazabilidades(request):
    """
    Vista que lista todos los lotes con su estado de trazabilidad.
    Muestra qué lotes tienen trazabilidad completa y cuáles no.
    """
    lotes = LoteCultivo.objects.prefetch_related('transformaciones__logisticas').all()
    
    # Agregar información de trazabilidad a cada lote
    lotes_con_info = []
    for lote in lotes:
        transformaciones = lote.transformaciones.all()
        logisticas = Logistica.objects.filter(transformacion__lote=lote)
        
        tiene_transformacion = transformaciones.exists()
        tiene_logistica = logisticas.exists()
        tiene_trazabilidad_completa = tiene_transformacion and tiene_logistica
        
        lotes_con_info.append({
            'lote': lote,
            'tiene_transformacion': tiene_transformacion,
            'tiene_logistica': tiene_logistica,
            'tiene_trazabilidad_completa': tiene_trazabilidad_completa,
            'num_transformaciones': transformaciones.count(),
            'num_logisticas': logisticas.count()
        })
    
    return render(request, 'proj/lista_trazabilidades.html', {
        'lotes_con_info': lotes_con_info
    })
