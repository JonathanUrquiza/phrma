# Sistema de Gestión de Stock Farmacéutico

## Descripción
Sistema Django REST API para gestión de stock farmacéutico con validación GTIN/EAN-13, control de lotes, fechas de vencimiento y sistema FEFO (First Expired First Out).

## Instalación y Configuración

### 1. Activar el entorno virtual e instalar dependencias

```bash
# Activar entorno virtual (Windows)
.\venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar la base de datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 3. Ejecutar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: http://127.0.0.1:8000/

## Credenciales preconfiguradas

- **Usuario:** admin
- **Contraseña:** admin123
- **Email:** admin@test.com

## API Endpoints

### Autenticación JWT
- `POST /api/token/` - Obtener token de acceso
- `POST /api/token/refresh/` - Refrescar token

### Productos
- `GET /api/productos/` - Listar productos
- `POST /api/productos/` - Crear producto
- `GET /api/productos/{id}/` - Obtener producto
- `PUT /api/productos/{id}/` - Actualizar producto
- `DELETE /api/productos/{id}/` - Eliminar producto

### Operaciones especiales
- `POST /api/productos/ingreso-scan/` - Ingreso por escaneo
- `POST /api/productos/{id}/egreso-fefo/` - Egreso FEFO
- `GET /api/scan/{codigo}/` - Buscar producto por código

### Lotes
- `GET /api/lotes/` - Listar lotes
- `POST /api/lotes/` - Crear lote
- `POST /api/lotes/{id}/ingreso/` - Ingreso a lote
- `POST /api/lotes/{id}/egreso/` - Egreso de lote
- `POST /api/lotes/{id}/ajuste/` - Ajuste de stock

### Movimientos
- `GET /api/movimientos/` - Listar movimientos (solo lectura)

### Reportes
- `GET /api/reportes/por_vencer/?dias=60` - Lotes por vencer

## Ejemplos de uso

### 1. Obtener token de autenticación
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Ingreso por escaneo
```bash
curl -X POST http://127.0.0.1:8000/api/productos/ingreso-scan/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "gtin": "7790001001234",
    "lote": "L001",
    "fecha_venc": "2025-12-31",
    "cantidad": 10,
    "motivo": "Compra"
  }'
```

### 3. Egreso FEFO
```bash
curl -X POST http://127.0.0.1:8000/api/productos/1/egreso-fefo/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "cantidad": 5,
    "motivo": "Venta",
    "documento_ref": "VENTA-001"
  }'
```

### 4. Consultar lotes por vencer
```bash
curl "http://127.0.0.1:8000/api/reportes/por_vencer/?dias=30"
```

## Funcionalidades principales

### Validación GTIN/EAN-13
- Valida códigos de barras con dígito verificador
- Únicos por producto

### Sistema FEFO
- Egreso automático por fecha de vencimiento más próxima
- Optimización de rotación de stock

### Control de stock
- Movimientos auditables (ingreso, egreso, ajuste)
- Stock por lote
- Validaciones de stock negativo

### Reportes
- Lotes próximos a vencer
- Historial completo de movimientos

## Panel de administración

Acceder a: http://127.0.0.1:8000/admin/

Usar las credenciales del superusuario para gestión completa del sistema.

## Archivos de datos

El proyecto incluye archivos JSON con datos de ejemplo:
- `datos_stock_fixed.json` - Datos de productos y stock
- `datos.json` - Datos adicionales

## Tecnologías utilizadas

- Django 5.2.6
- Django REST Framework 3.16.1
- JWT Authentication
- SQLite (desarrollo) / PostgreSQL (producción)
- Python 3.12+
