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
from .models import LoteCultivo, Transformacion, Logistica, Auditoria
from .forms import LoteCultivoForm, TransformacionForm, LogisticaForm
from .business_logic.validaciones import ServicioTrazabilidad, ValidacionTrazabilidadError
from .utils import registrar_auditoria


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
            # Registrar auditoría
            registrar_auditoria(
                tipo_entidad=Auditoria.TIPO_LOTE,
                entidad_id=lote.id,
                accion=Auditoria.ACCION_CREAR,
                descripcion=f'Lote de cultivo "{lote.codigo_lote}" creado',
                request=request
            )
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


def editar_lote(request, pk):
    """
    Vista para editar un lote de cultivo existente.
    
    Permite actualizar los datos del lote y registra los cambios en auditoría.
    """
    lote = get_object_or_404(LoteCultivo, pk=pk)
    
    if request.method == 'POST':
        form = LoteCultivoForm(request.POST, instance=lote)
        if form.is_valid():
            # Detectar cambios importantes antes de guardar
            cambios = []
            for field in form.changed_data:
                old_value = getattr(lote, field, None)
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    cambios.append({
                        'campo': field,
                        'anterior': old_value,
                        'nuevo': new_value
                    })
            
            lote_actualizado = form.save()
            
            # Registrar auditoría para cada cambio
            if cambios:
                for cambio in cambios:
                    registrar_auditoria(
                        tipo_entidad=Auditoria.TIPO_LOTE,
                        entidad_id=lote_actualizado.id,
                        accion=Auditoria.ACCION_ACTUALIZAR,
                        campo_modificado=cambio['campo'],
                        valor_anterior=cambio['anterior'],
                        valor_nuevo=cambio['nuevo'],
                        descripcion=f'Lote "{lote_actualizado.codigo_lote}": {cambio["campo"]} actualizado',
                        request=request
                    )
            else:
                registrar_auditoria(
                    tipo_entidad=Auditoria.TIPO_LOTE,
                    entidad_id=lote_actualizado.id,
                    accion=Auditoria.ACCION_ACTUALIZAR,
                    descripcion=f'Lote "{lote_actualizado.codigo_lote}" actualizado',
                    request=request
                )
            
            messages.success(
                request,
                f'Lote de cultivo "{lote_actualizado.codigo_lote}" actualizado exitosamente.'
            )
            return redirect('detalle_lote', pk=lote_actualizado.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LoteCultivoForm(instance=lote)
    
    return render(request, 'proj/lote_form.html', {
        'form': form,
        'titulo': 'Editar Lote de Cultivo',
        'accion': 'Actualizar',
        'lote': lote
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
    
    # Obtener historial de auditoría del lote
    historial_lote = Auditoria.objects.filter(
        tipo_entidad=Auditoria.TIPO_LOTE,
        entidad_id=lote.id
    ).order_by('-fecha_cambio')[:10]
    
    # Obtener historial de transformaciones relacionadas
    historial_transformaciones = []
    for trans in transformaciones:
        historial = Auditoria.objects.filter(
            tipo_entidad=Auditoria.TIPO_TRANSFORMACION,
            entidad_id=trans.id
        ).order_by('-fecha_cambio')[:5]
        historial_transformaciones.append({
            'transformacion': trans,
            'historial': historial
        })
    
    # Obtener historial de logísticas relacionadas
    historial_logisticas = []
    for log in logisticas:
        historial = Auditoria.objects.filter(
            tipo_entidad=Auditoria.TIPO_LOGISTICA,
            entidad_id=log.id
        ).order_by('-fecha_cambio')[:5]
        historial_logisticas.append({
            'logistica': log,
            'historial': historial
        })
    
    return render(request, 'proj/detalle_lote.html', {
        'lote': lote,
        'transformaciones': transformaciones,
        'logisticas': logisticas,
        'historial_lote': historial_lote,
        'historial_transformaciones': historial_transformaciones,
        'historial_logisticas': historial_logisticas
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
            # Registrar auditoría
            registrar_auditoria(
                tipo_entidad=Auditoria.TIPO_TRANSFORMACION,
                entidad_id=transformacion.id,
                accion=Auditoria.ACCION_CREAR,
                descripcion=f'Transformación creada para lote "{transformacion.lote.codigo_lote}"',
                request=request
            )
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


def editar_transformacion(request, pk):
    """
    Vista para editar una transformación existente.
    
    Permite actualizar los datos de la transformación y registra los cambios.
    """
    transformacion = get_object_or_404(Transformacion, pk=pk)
    
    if request.method == 'POST':
        form = TransformacionForm(request.POST, instance=transformacion)
        if form.is_valid():
            # Detectar cambios importantes antes de guardar
            cambios = []
            for field in form.changed_data:
                old_value = getattr(transformacion, field, None)
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    cambios.append({
                        'campo': field,
                        'anterior': old_value,
                        'nuevo': new_value
                    })
            
            transformacion_actualizada = form.save()
            
            # Registrar auditoría para cada cambio
            if cambios:
                for cambio in cambios:
                    registrar_auditoria(
                        tipo_entidad=Auditoria.TIPO_TRANSFORMACION,
                        entidad_id=transformacion_actualizada.id,
                        accion=Auditoria.ACCION_ACTUALIZAR,
                        campo_modificado=cambio['campo'],
                        valor_anterior=cambio['anterior'],
                        valor_nuevo=cambio['nuevo'],
                        descripcion=f'Transformación (Lote: {transformacion_actualizada.lote.codigo_lote}): {cambio["campo"]} actualizado',
                        request=request
                    )
            else:
                registrar_auditoria(
                    tipo_entidad=Auditoria.TIPO_TRANSFORMACION,
                    entidad_id=transformacion_actualizada.id,
                    accion=Auditoria.ACCION_ACTUALIZAR,
                    descripcion=f'Transformación (Lote: {transformacion_actualizada.lote.codigo_lote}) actualizada',
                    request=request
                )
            
            messages.success(
                request,
                f'Transformación para el lote "{transformacion_actualizada.lote.codigo_lote}" actualizada exitosamente.'
            )
            return redirect('lista_transformaciones')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = TransformacionForm(instance=transformacion)
    
    return render(request, 'proj/transformacion_form.html', {
        'form': form,
        'titulo': 'Editar Transformación',
        'accion': 'Actualizar',
        'transformacion': transformacion
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
                # Registrar auditoría
                registrar_auditoria(
                    tipo_entidad=Auditoria.TIPO_LOGISTICA,
                    entidad_id=logistica.id,
                    accion=Auditoria.ACCION_CREAR,
                    descripcion=f'Logística "{logistica.numero_guia}" creada',
                    request=request
                )
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


def editar_logistica(request, pk):
    """
    Vista para editar un registro de logística existente.
    
    Permite actualizar los datos de la logística, especialmente el estado
    para que se genere el código de trazabilidad cuando se marca como ENTREGADO.
    """
    logistica = get_object_or_404(Logistica, pk=pk)
    
    if request.method == 'POST':
        form = LogisticaForm(request.POST, instance=logistica)
        if form.is_valid():
            # Validar trazabilidad completa
            try:
                transformacion = form.cleaned_data['transformacion']
                lote = transformacion.lote
                logistica_actualizada = form.save(commit=False)
                
                # Validar trazabilidad completa usando servicio de negocio
                ServicioTrazabilidad.validar_trazabilidad_completa(
                    lote,
                    transformacion,
                    logistica_actualizada
                )
                
                # Detectar cambios importantes
                estado_anterior = logistica.estado if logistica.pk else None
                codigo_anterior = logistica.codigo_trazabilidad if logistica.pk else None
                
                # Si cambió a ENTREGADO, el código se generará en save()
                logistica_actualizada.save()
                
                # Registrar auditoría
                descripcion = f'Logística "{logistica_actualizada.numero_guia}" actualizada'
                if estado_anterior != logistica_actualizada.estado:
                    registrar_auditoria(
                        tipo_entidad=Auditoria.TIPO_LOGISTICA,
                        entidad_id=logistica_actualizada.id,
                        accion=Auditoria.ACCION_ACTUALIZAR,
                        campo_modificado='estado',
                        valor_anterior=estado_anterior,
                        valor_nuevo=logistica_actualizada.estado,
                        descripcion=f'{descripcion}: Estado cambiado de {estado_anterior} a {logistica_actualizada.estado}',
                        request=request
                    )
                else:
                    registrar_auditoria(
                        tipo_entidad=Auditoria.TIPO_LOGISTICA,
                        entidad_id=logistica_actualizada.id,
                        accion=Auditoria.ACCION_ACTUALIZAR,
                        descripcion=descripcion,
                        request=request
                    )
                
                # Registrar si se generó código de trazabilidad
                if logistica_actualizada.codigo_trazabilidad and codigo_anterior != logistica_actualizada.codigo_trazabilidad:
                    registrar_auditoria(
                        tipo_entidad=Auditoria.TIPO_LOGISTICA,
                        entidad_id=logistica_actualizada.id,
                        accion=Auditoria.ACCION_ACTUALIZAR,
                        campo_modificado='codigo_trazabilidad',
                        valor_anterior=codigo_anterior,
                        valor_nuevo=logistica_actualizada.codigo_trazabilidad,
                        descripcion=f'Código de trazabilidad generado: {logistica_actualizada.codigo_trazabilidad}',
                        request=request
                    )
                    messages.info(
                        request,
                        f'Código de trazabilidad generado: {logistica_actualizada.codigo_trazabilidad}'
                    )
                
                messages.success(
                    request,
                    f'Logística "{logistica_actualizada.numero_guia}" actualizada exitosamente.'
                )
                return redirect('lista_logisticas')
            except ValidacionTrazabilidadError as e:
                messages.error(request, f'Error de validación: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LogisticaForm(instance=logistica)
    
    return render(request, 'proj/logistica_form.html', {
        'form': form,
        'titulo': 'Editar Logística',
        'accion': 'Actualizar',
        'logistica': logistica
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
    
    # Obtener historial de auditoría completo
    historial_lote = Auditoria.objects.filter(
        tipo_entidad=Auditoria.TIPO_LOTE,
        entidad_id=lote.id
    ).order_by('-fecha_cambio')[:10]
    
    # Historial de transformaciones y logísticas
    historial_completo = []
    for transformacion in transformaciones:
        historial_trans = Auditoria.objects.filter(
            tipo_entidad=Auditoria.TIPO_TRANSFORMACION,
            entidad_id=transformacion.id
        ).order_by('-fecha_cambio')[:5]
        historial_completo.extend(historial_trans)
    
    for logistica in logisticas:
        historial_log = Auditoria.objects.filter(
            tipo_entidad=Auditoria.TIPO_LOGISTICA,
            entidad_id=logistica.id
        ).order_by('-fecha_cambio')[:5]
        historial_completo.extend(historial_log)
    
    # Ordenar todo el historial por fecha
    historial_completo = sorted(historial_completo, key=lambda x: x.fecha_cambio, reverse=True)[:15]
    
    return render(request, 'proj/trazabilidad_completa.html', {
        'lote': lote,
        'transformaciones': transformaciones,
        'logisticas': logisticas,
        'errores_validacion': errores_validacion,
        'historial_lote': historial_lote,
        'historial_completo': historial_completo
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


def buscar_por_codigo(request):
    """
    Vista para buscar trazabilidad completa por código QR/trazabilidad.
    
    Permite a los usuarios (incluyendo consumidores) buscar información
    usando el código de trazabilidad del empaque.
    """
    codigo = request.GET.get('codigo', '').strip()
    logistica = None
    lote = None
    transformacion = None
    
    if codigo:
        try:
            logistica = Logistica.objects.select_related(
                'transformacion__lote'
            ).get(codigo_trazabilidad=codigo)
            transformacion = logistica.transformacion
            lote = transformacion.lote
        except Logistica.DoesNotExist:
            messages.error(request, f'No se encontró trazabilidad para el código: {codigo}')
    
    return render(request, 'proj/buscar_trazabilidad.html', {
        'codigo': codigo,
        'logistica': logistica,
        'transformacion': transformacion,
        'lote': lote
    })
