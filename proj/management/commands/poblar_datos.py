"""
Comando de Django para poblar la base de datos con datos de prueba.

Uso:
    python manage.py poblar_datos

Este comando crea:
- Múltiples lotes de cultivo
- Transformaciones asociadas
- Logísticas completas
- Varias variantes para probar diferentes escenarios
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import random

from proj.models import LoteCultivo, Transformacion, Logistica


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba para el sistema de trazabilidad'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=12,
            help='Número de trazabilidades completas a crear (default: 12)',
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los datos existentes antes de poblar',
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        limpiar = options['limpiar']

        if limpiar:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            Logistica.objects.all().delete()
            Transformacion.objects.all().delete()
            LoteCultivo.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Datos eliminados correctamente.'))

        self.stdout.write(self.style.SUCCESS(f'Creando {cantidad} trazabilidades...'))

        # Tipos de productos
        tipos_productos = [
            'Mango Orgánico',
            'Mango Tommy Atkins',
            'Mango Ataulfo',
            'Aguacate Hass',
            'Limón Persa',
            'Naranja Valencia',
        ]

        # Ubicaciones
        ubicaciones = [
            'Finca San José, Valle Central',
            'Finca Los Pinos, Guanacaste',
            'Finca El Roble, Cartago',
            'Finca La Esperanza, Alajuela',
            'Finca Santa Fe, Puntarenas',
            'Finca Los Mangos, Limón',
        ]

        # Responsables
        responsables = [
            'Juan Pérez',
            'María González',
            'Carlos Ramírez',
            'Ana Martínez',
            'Roberto Sánchez',
            'Laura Fernández',
        ]

        # Supermercados destino
        supermercados = [
            'Supermercado Central',
            'Walmart Costa Rica',
            'Auto Mercado',
            'Palí',
            'Mas x Menos',
            'Super Compro',
        ]

        # Fechas base (hace 30 días)
        fecha_base = timezone.now().date() - timedelta(days=30)

        # Obtener el último número de lote existente para evitar duplicados
        ultimo_lote = LoteCultivo.objects.order_by('-codigo_lote').first()
        if ultimo_lote:
            # Extraer el número del último código (ej: LOTE-2024-012 -> 12)
            try:
                ultimo_numero = int(ultimo_lote.codigo_lote.split('-')[-1])
                inicio_numero = ultimo_numero + 1
            except (ValueError, IndexError):
                inicio_numero = 1
        else:
            inicio_numero = 1

        lotes_creados = []
        transformaciones_creadas = []
        logisticas_creadas = []

        # Crear trazabilidades completas
        for i in range(cantidad):
            numero_lote = inicio_numero + i
            # Variaciones: algunas completas, algunas parciales
            tiene_transformacion = True
            tiene_logistica = True if i < cantidad * 0.8 else False  # 80% tienen logística
            
            # Crear lote
            fecha_cosecha = fecha_base - timedelta(days=random.randint(0, 20))
            
            codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}'
            
            # Verificar si ya existe (por si acaso)
            if LoteCultivo.objects.filter(codigo_lote=codigo_lote).exists():
                codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}-{random.randint(100, 999)}'
            
            lote = LoteCultivo.objects.create(
                codigo_lote=codigo_lote,
                tipo_producto=random.choice(tipos_productos),
                ubicacion=random.choice(ubicaciones),
                area_hectareas=Decimal(str(round(random.uniform(2.5, 15.0), 2))),
                fecha_cosecha=fecha_cosecha,
                responsable=random.choice(responsables),
            )
            lotes_creados.append(lote)
            self.stdout.write(f'  ✓ Lote creado: {lote.codigo_lote}')

            if tiene_transformacion:
                # Crear transformación
                # Fechas: lavado 1 día después de cosecha, empaquetado 2 días, control 3 días
                fecha_lavado = timezone.make_aware(
                    datetime.combine(fecha_cosecha + timedelta(days=1), datetime.min.time().replace(hour=8))
                )
                fecha_empaquetado = fecha_lavado + timedelta(hours=6)
                fecha_control = fecha_empaquetado + timedelta(hours=4)

                # Resultados de calidad variados
                resultados_calidad = ['APROBADO', 'APROBADO', 'APROBADO', 'CONDICIONAL', 'RECHAZADO']
                resultado = random.choice(resultados_calidad)

                transformacion = Transformacion.objects.create(
                    lote=lote,
                    fecha_lavado=fecha_lavado,
                    temperatura_lavado=Decimal(str(round(random.uniform(15.0, 30.0), 2))),
                    responsable_lavado=random.choice(responsables),
                    fecha_empaquetado=fecha_empaquetado,
                    tipo_empaque=random.choice(['Caja de cartón', 'Bolsa plástica', 'Canasta de plástico', 'Caja de madera']),
                    cantidad_unidades=random.randint(500, 5000),
                    responsable_empaquetado=random.choice(responsables),
                    fecha_control_calidad=fecha_control,
                    resultado_calidad=resultado,
                    observaciones_calidad='Control de calidad realizado según protocolo' if resultado == 'APROBADO' else 'Se requieren ajustes',
                    responsable_calidad=random.choice(responsables),
                )
                transformaciones_creadas.append(transformacion)
                self.stdout.write(f'    ✓ Transformación creada (Calidad: {resultado})')

                if tiene_logistica and resultado != 'RECHAZADO':
                    # Crear logística
                    fecha_salida = fecha_control + timedelta(hours=2)
                    # Tiempo de transporte entre 8 y 48 horas
                    tiempo_transporte = timedelta(hours=random.randint(8, 48))
                    fecha_entrega = fecha_salida + tiempo_transporte

                    # Temperaturas dentro del rango permitido (2-8°C)
                    temp_min = Decimal(str(round(random.uniform(2.0, 5.0), 2)))
                    temp_max = Decimal(str(round(random.uniform(5.5, 8.0), 2)))
                    temp_promedio = Decimal(str(round((temp_min + temp_max) / 2, 2)))

                    # Algunos casos con problemas de temperatura (para pruebas)
                    if i % 5 == 0:  # 20% tienen problemas
                        temp_max = Decimal(str(round(random.uniform(8.5, 12.0), 2)))
                        temp_promedio = Decimal(str(round((temp_min + temp_max) / 2, 2)))

                    # Estados variados
                    estados = ['ENTREGADO', 'ENTREGADO', 'ENTREGADO', 'EN_TRANSITO', 'RETRASADO']
                    estado = random.choice(estados)

                    numero_guia = f'GUI-2024-{str(numero_lote).zfill(4)}'
                    # Verificar si ya existe la guía
                    if Logistica.objects.filter(numero_guia=numero_guia).exists():
                        numero_guia = f'GUI-2024-{str(numero_lote).zfill(4)}-{random.randint(10, 99)}'

                    logistica = Logistica.objects.create(
                        transformacion=transformacion,
                        numero_guia=numero_guia,
                        vehiculo=f'ABC-{random.randint(100, 999)}',
                        conductor=random.choice(responsables),
                        temperatura_minima=temp_min,
                        temperatura_maxima=temp_max,
                        temperatura_promedio=temp_promedio,
                        fecha_salida=fecha_salida,
                        fecha_entrega=fecha_entrega,
                        destino=random.choice(supermercados),
                        direccion_destino=f'Dirección del {random.choice(supermercados)}, {random.choice(["San José", "Alajuela", "Cartago", "Heredia"])}',
                        estado=estado,
                    )
                    logisticas_creadas.append(logistica)
                    self.stdout.write(f'      ✓ Logística creada (Estado: {estado})')

        # Crear algunos lotes sin transformación (para variar)
        for i in range(3):
            numero_lote = inicio_numero + cantidad + i
            fecha_cosecha = fecha_base - timedelta(days=random.randint(0, 15))
            
            codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}'
            if LoteCultivo.objects.filter(codigo_lote=codigo_lote).exists():
                codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}-{random.randint(100, 999)}'
            
            lote = LoteCultivo.objects.create(
                codigo_lote=codigo_lote,
                tipo_producto=random.choice(tipos_productos),
                ubicacion=random.choice(ubicaciones),
                area_hectareas=Decimal(str(round(random.uniform(2.5, 10.0), 2))),
                fecha_cosecha=fecha_cosecha,
                responsable=random.choice(responsables),
            )
            lotes_creados.append(lote)
            self.stdout.write(f'  ✓ Lote creado (sin transformación): {lote.codigo_lote}')

        # Crear algunos lotes con transformación pero sin logística
        for i in range(2):
            numero_lote = inicio_numero + cantidad + 3 + i
            fecha_cosecha = fecha_base - timedelta(days=random.randint(0, 10))
            
            codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}'
            if LoteCultivo.objects.filter(codigo_lote=codigo_lote).exists():
                codigo_lote = f'LOTE-2024-{str(numero_lote).zfill(3)}-{random.randint(100, 999)}'
            
            lote = LoteCultivo.objects.create(
                codigo_lote=codigo_lote,
                tipo_producto=random.choice(tipos_productos),
                ubicacion=random.choice(ubicaciones),
                area_hectareas=Decimal(str(round(random.uniform(3.0, 12.0), 2))),
                fecha_cosecha=fecha_cosecha,
                responsable=random.choice(responsables),
            )
            lotes_creados.append(lote)

            fecha_lavado = timezone.make_aware(
                datetime.combine(fecha_cosecha + timedelta(days=1), datetime.min.time().replace(hour=9))
            )
            fecha_empaquetado = fecha_lavado + timedelta(hours=5)
            fecha_control = fecha_empaquetado + timedelta(hours=3)

            transformacion = Transformacion.objects.create(
                lote=lote,
                fecha_lavado=fecha_lavado,
                temperatura_lavado=Decimal(str(round(random.uniform(18.0, 28.0), 2))),
                responsable_lavado=random.choice(responsables),
                fecha_empaquetado=fecha_empaquetado,
                tipo_empaque=random.choice(['Caja de cartón', 'Bolsa plástica']),
                cantidad_unidades=random.randint(800, 3000),
                responsable_empaquetado=random.choice(responsables),
                fecha_control_calidad=fecha_control,
                resultado_calidad='APROBADO',
                observaciones_calidad='Pendiente de transporte',
                responsable_calidad=random.choice(responsables),
            )
            self.stdout.write(f'  ✓ Lote creado (con transformación, sin logística): {lote.codigo_lote}')

        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\n✅ Datos poblados correctamente!\n'))
        self.stdout.write(f'  📦 Lotes de Cultivo: {len(lotes_creados)}')
        self.stdout.write(f'  ⚙️  Transformaciones: {Transformacion.objects.count()}')
        self.stdout.write(f'  🚚 Logísticas: {Logistica.objects.count()}')
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\n💡 Puedes acceder al sistema en: http://127.0.0.1:8000/'))
        self.stdout.write(self.style.SUCCESS('💡 Ejecuta el servidor con: python manage.py runserver\n'))

