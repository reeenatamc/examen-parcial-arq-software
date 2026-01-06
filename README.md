# Sistema de Trazabilidad Agrícola

Sistema para garantizar la trazabilidad de productos agrícolas (como mangos orgánicos) desde la cosecha hasta que llegan al supermercado. Desarrollado con Django utilizando una **Arquitectura de 3 Capas Estricta**.

## 📋 Descripción del Proyecto

Este sistema permite registrar y rastrear la información completa de los productos agrícolas a través de tres etapas principales:

1. **Origen**: Datos del lote de cultivo y fecha de cosecha
2. **Transformación**: Datos de lavado, empaquetado y controles de calidad
3. **Logística**: Registro de temperatura durante el transporte y fecha de entrega

## 🏗️ Arquitectura de 3 Capas Estricta

El proyecto está organizado siguiendo una arquitectura de 3 capas estricta:

### 1. **Capa de Datos** (`proj/models.py`)
- Utiliza Django ORM para definir los modelos de datos
- Modelos principales:
  - `LoteCultivo`: Información del lote de cultivo y cosecha
  - `Transformacion`: Procesos de lavado, empaquetado y control de calidad
  - `Logistica`: Información de transporte y entrega

### 2. **Capa de Lógica de Negocio** (`proj/business_logic/`)
- Contiene todas las reglas de negocio y validaciones
- Validadores:
  - `ValidadorLoteCultivo`: Valida códigos de lote y fechas de cosecha
  - `ValidadorTransformacion`: Valida temperaturas de lavado, secuencia de fechas y cantidades
  - `ValidadorLogistica`: Valida temperaturas de transporte y fechas
  - `ServicioTrazabilidad`: Coordina validaciones de trazabilidad completa

### 3. **Capa de Presentación** (`proj/views.py`, `proj/forms.py`, `proj/templates/`)
- Vistas Django que manejan las peticiones HTTP
- Formularios para capturar datos del usuario
- Templates HTML para la interfaz de usuario
- Integración con Bootstrap para una UI moderna

## 🚀 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

## 📦 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <https://github.com/reeenatamc/examen-parcial-arq-software>
cd examen-parcial-arq-software
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```


### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear un superusuario (opcional, para acceder al admin)

```bash
python manage.py createsuperuser
```

### 6. Poblar la base de datos con datos de prueba (opcional pero recomendado)

```bash
python manage.py poblar_datos
```

Este comando crea:
- 12 trazabilidades completas (por defecto)
- Lotes con transformaciones y logísticas
- Varios estados y tipos de productos
- Casos variados para probar el sistema

Opciones del comando:
```bash
# Crear más trazabilidades
python manage.py poblar_datos --cantidad 20

# Limpiar datos existentes antes de poblar
python manage.py poblar_datos --limpiar
```

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en `http://127.0.0.1:8000/`

## 💻 Uso del Sistema

### Acceso a la Aplicación

1. Abre tu navegador y ve a `http://127.0.0.1:8000/`
2. Verás el dashboard principal con estadísticas y enlaces a las diferentes secciones

### Flujo de Trabajo

#### 1. Registrar un Lote de Cultivo (Origen)

1. Ve a **Origen > Crear Lote** o haz clic en el botón "Crear Nuevo Lote" en el dashboard
2. Completa el formulario:
   - **Código del Lote**: Debe comenzar con letra y tener al menos 3 caracteres (ej: `LOTE-2024-001`)
   - **Tipo de Producto**: Ejemplo: "Mango Orgánico"
   - **Ubicación**: Ubicación geográfica del lote
   - **Área**: En hectáreas
   - **Fecha de Cosecha**: No puede ser una fecha futura
   - **Responsable**: Nombre del responsable
3. Haz clic en "Crear"
4. El sistema validará los datos usando la capa de lógica de negocio

#### 2. Registrar una Transformación

1. Ve a **Transformación > Crear Transformación**
2. Selecciona el lote de cultivo asociado
3. Completa los datos de:
   - **Lavado**: Fecha, temperatura (debe estar entre 10°C y 40°C) y responsable
   - **Empaquetado**: Fecha, tipo de empaque, cantidad de unidades y responsable
   - **Control de Calidad**: Fecha, resultado (Aprobado/Rechazado/Condicional), observaciones y responsable
4. El sistema validará que las fechas estén en el orden correcto: Lavado → Empaquetado → Control de Calidad
5. Haz clic en "Crear"

#### 3. Registrar Logística (Transporte)

1. Ve a **Logística > Crear Logística**
2. Selecciona la transformación asociada
3. Completa los datos:
   - **Número de Guía**: Debe tener al menos 5 caracteres
   - **Vehículo y Conductor**: Información del transporte
   - **Temperaturas**: Mínima, máxima y promedio (deben estar entre 2°C y 8°C)
   - **Fechas**: Salida y entrega (la entrega debe ser posterior a la salida)
   - **Destino**: Información del supermercado
   - **Estado**: En Tránsito, Entregado o Retrasado
4. El sistema validará:
   - Que las temperaturas estén en el rango permitido
   - Que las fechas sean coherentes
   - Que el tiempo de transporte no exceda 72 horas
5. Haz clic en "Crear"

#### 4. Ver Trazabilidad Completa

1. Desde la lista de lotes, haz clic en "Trazabilidad" o "Ver Trazabilidad Completa"
2. Verás el flujo completo: Origen → Transformación → Logística
3. El sistema mostrará errores de validación si existen inconsistencias

### Validaciones del Sistema

El sistema aplica las siguientes validaciones (Capa de Lógica de Negocio):

- **Código de Lote**: Debe comenzar con letra y tener al menos 3 caracteres
- **Fecha de Cosecha**: No puede ser una fecha futura
- **Temperatura de Lavado**: Debe estar entre 10°C y 40°C
- **Secuencia de Fechas**: Lavado → Empaquetado → Control de Calidad (en orden)
- **Cantidad de Unidades**: Debe ser mayor a 0 y no exceder 100,000
- **Temperaturas de Transporte**: Deben estar entre 2°C y 8°C
- **Fechas de Transporte**: La entrega debe ser posterior a la salida y el tiempo no debe exceder 72 horas
- **Trazabilidad Completa**: Valida la coherencia de toda la cadena de trazabilidad

## 📁 Estructura del Proyecto

```
examen-parcial-arq-software/
├── manage.py
├── db.sqlite3                    # Base de datos SQLite
├── README.md
├── proj/                         # Aplicación principal
│   ├── __init__.py
│   ├── admin.py                  # Registro de modelos en admin
│   ├── apps.py
│   ├── forms.py                  # Capa de Presentación: Formularios
│   ├── models.py                 # Capa de Datos: Modelos Django ORM
│   ├── views.py                  # Capa de Presentación: Vistas
│   ├── urls.py                   # Configuración de URLs
│   ├── business_logic/           # Capa de Lógica de Negocio
│   │   ├── __init__.py
│   │   └── validaciones.py       # Validadores y reglas de negocio
│   └── templates/
│       └── proj/                 # Templates HTML
│           ├── base.html
│           ├── index.html
│           ├── lote_form.html
│           ├── lista_lotes.html
│           ├── detalle_lote.html
│           ├── transformacion_form.html
│           ├── lista_transformaciones.html
│           ├── logistica_form.html
│           ├── lista_logisticas.html
│           └── trazabilidad_completa.html
└── projexamen/                   # Configuración del proyecto Django
    ├── __init__.py
    ├── settings.py               # Configuración de Django
    ├── urls.py                   # URLs principales
    ├── wsgi.py
    └── asgi.py
```

## 🗄️ Estructura de la Base de Datos

### Tabla: `proj_lotecultivo`
- `id`: Clave primaria
- `codigo_lote`: Código único del lote
- `tipo_producto`: Tipo de producto (ej: Mango Orgánico)
- `ubicacion`: Ubicación del lote
- `area_hectareas`: Área en hectáreas
- `fecha_cosecha`: Fecha de cosecha
- `responsable`: Responsable del lote
- `fecha_creacion`: Fecha de creación del registro
- `fecha_actualizacion`: Fecha de última actualización

### Tabla: `proj_transformacion`
- `id`: Clave primaria
- `lote_id`: Clave foránea a `proj_lotecultivo`
- `fecha_lavado`: Fecha y hora del lavado
- `temperatura_lavado`: Temperatura del agua de lavado
- `responsable_lavado`: Responsable del lavado
- `fecha_empaquetado`: Fecha y hora del empaquetado
- `tipo_empaque`: Tipo de empaque utilizado
- `cantidad_unidades`: Cantidad de unidades empacadas
- `responsable_empaquetado`: Responsable del empaquetado
- `fecha_control_calidad`: Fecha y hora del control de calidad
- `resultado_calidad`: Resultado (APROBADO/RECHAZADO/CONDICIONAL)
- `observaciones_calidad`: Observaciones del control
- `responsable_calidad`: Responsable del control de calidad
- `fecha_creacion`: Fecha de creación
- `fecha_actualizacion`: Fecha de última actualización

### Tabla: `proj_logistica`
- `id`: Clave primaria
- `transformacion_id`: Clave foránea a `proj_transformacion`
- `numero_guia`: Número único de guía de transporte
- `vehiculo`: Identificación del vehículo
- `conductor`: Nombre del conductor
- `temperatura_minima`: Temperatura mínima registrada
- `temperatura_maxima`: Temperatura máxima registrada
- `temperatura_promedio`: Temperatura promedio
- `fecha_salida`: Fecha y hora de salida
- `fecha_entrega`: Fecha y hora de entrega
- `destino`: Nombre del supermercado/destino
- `direccion_destino`: Dirección completa del destino
- `estado`: Estado (EN_TRANSITO/ENTREGADO/RETRASADO)
- `fecha_creacion`: Fecha de creación
- `fecha_actualizacion`: Fecha de última actualización

## 🧪 Ejemplos de Uso

### Ejemplo 1: Crear un lote completo

1. **Crear Lote**:
   - Código: `LOTE-2024-001`
   - Producto: `Mango Orgánico`
   - Ubicación: `Finca San José, Valle Central`
   - Área: `5.50` hectáreas
   - Fecha de Cosecha: `2024-01-15`
   - Responsable: `Juan Pérez`

2. **Crear Transformación**:
   - Lote: `LOTE-2024-001`
   - Lavado: `2024-01-16 08:00`, temperatura `25°C`
   - Empaquetado: `2024-01-16 14:00`, `Caja de cartón`, `1000 unidades`
   - Control de Calidad: `2024-01-16 16:00`, resultado `APROBADO`

3. **Crear Logística**:
   - Transformación: (la creada anteriormente)
   - Número de Guía: `GUI-2024-001`
   - Temperaturas: Min `3°C`, Max `6°C`, Promedio `4.5°C`
   - Salida: `2024-01-17 06:00`
   - Entrega: `2024-01-17 12:00`
   - Destino: `Supermercado Central`

### Ejemplo 2: Ver trazabilidad completa

1. Ve a la lista de lotes
2. Haz clic en "Trazabilidad" junto al lote `LOTE-2024-001`
3. Verás el flujo completo con toda la información registrada

## 🔧 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Acceder a la shell de Django
python manage.py shell

# Limpiar base de datos (eliminar todas las tablas)
rm db.sqlite3
python manage.py migrate
```

## 📝 Características Técnicas

- **Framework**: Django 6.0.1
- **Base de Datos**: SQLite (por defecto)
- **Frontend**: Bootstrap 5.3.0
- **Iconos**: Bootstrap Icons
- **Arquitectura**: 3 Capas Estricta (Presentación, Lógica de Negocio, Datos)

## 📚 Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)

## 👤 Autor

Sistema desarrollado como examen parcial de Arquitectura de Software por Renata Maldonado <3.

## 📄 Licencia

Este proyecto es de uso educativo.

---

**Nota**: Este sistema implementa una arquitectura de 3 capas estricta donde:
- La **Capa de Datos** solo contiene modelos y acceso a base de datos
- La **Capa de Lógica de Negocio** contiene todas las reglas y validaciones
- La **Capa de Presentación** solo maneja la interfaz de usuario y delega la lógica a la capa de negocio
