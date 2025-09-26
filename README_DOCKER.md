# 🐳 Despliegue con Docker en Render

Esta aplicación Django está completamente configurada para desplegarse en Render usando Docker.

## 📋 Archivos Docker incluidos

- **`Dockerfile`** - Imagen multi-stage optimizada para producción
- **`docker-compose.yml`** - Para desarrollo local con PostgreSQL
- **`docker-compose.prod.yml`** - Para producción con variables de entorno
- **`docker-entrypoint.sh`** - Script de inicialización
- **`.dockerignore`** - Optimiza el build excluyendo archivos innecesarios

## 🚀 Desplegar en Render

### Opción 1: Despliegue automático (Recomendado)

1. **Subir a GitHub**: Asegúrate de que tu código esté en un repositorio GitHub
2. **Conectar en Render**:
   - Ve a [render.com](https://render.com)
   - Crea una nueva cuenta o inicia sesión
   - Selecciona "New +" → "Web Service"
   - Conecta tu repositorio GitHub

3. **Configurar el servicio**:
   - **Environment**: Docker
   - **Build Command**: (se detecta automáticamente el Dockerfile)
   - **Start Command**: (se usa el CMD del Dockerfile)

4. **Variables de entorno requeridas**:
   ```
   SECRET_KEY=tu-clave-secreta-aqui
   DEBUG=false
   ALLOWED_HOSTS=tu-app-nombre.onrender.com
   DATABASE_URL=(se configura automáticamente con la BD de Render)
   ```

5. **Crear base de datos PostgreSQL**:
   - En Render: "New +" → "PostgreSQL"
   - Nombre: `pharma-db`
   - La `DATABASE_URL` se conectará automáticamente

### Opción 2: Render Blueprint (Configuración automática)

Usa el archivo `render.yaml` incluido:

1. En Render: "New +" → "Blueprint"
2. Conecta tu repositorio
3. Render detectará automáticamente `render.yaml` y creará:
   - Servicio web con Docker
   - Base de datos PostgreSQL
   - Variables de entorno automáticas

## 💻 Desarrollo Local

### Prerrequisitos
- Docker y Docker Compose instalados

### Desarrollo con SQLite (rápido)
```bash
# Construir y ejecutar
docker build -t pharma-app .
docker run -p 8000:8000 -e DEBUG=true pharma-app

# Acceder a la aplicación
# http://localhost:8000
```

### Desarrollo con PostgreSQL (completo)
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Acceder al contenedor
docker-compose exec web bash

# Ejecutar comandos Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Parar servicios
docker-compose down

# Limpiar volúmenes (⚠️ elimina datos)
docker-compose down -v
```

## 🔧 Comandos útiles

### Construir imagen manualmente
```bash
docker build -t pharma-app .
```

### Ejecutar con variables personalizadas
```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="tu-clave" \
  -e DEBUG=false \
  -e DATABASE_URL="postgres://..." \
  pharma-app
```

### Ejecutar comandos Django en contenedor
```bash
# Migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Shell de Django
docker-compose exec web python manage.py shell

# Collectstatic
docker-compose exec web python manage.py collectstatic
```

## 🔒 Variables de Entorno para Producción

Copia `env.example` a `.env` y configura:

```bash
# Generar SECRET_KEY nueva
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Variables importantes:
- **`SECRET_KEY`**: ⚠️ OBLIGATORIO - Genera una nueva para producción
- **`DEBUG`**: Debe ser `false` en producción
- **`DATABASE_URL`**: Render la proporciona automáticamente
- **`ALLOWED_HOSTS`**: Tu dominio de Render (ej: `mi-app.onrender.com`)

## 📊 URLs disponibles una vez desplegado

- **Admin**: `https://tu-app.onrender.com/admin/`
- **API Base**: `https://tu-app.onrender.com/api/`
- **Productos**: `https://tu-app.onrender.com/api/productos/`
- **Lotes**: `https://tu-app.onrender.com/api/lotes/`
- **Movimientos**: `https://tu-app.onrender.com/api/movimientos/`
- **Escaner**: `https://tu-app.onrender.com/api/scan/{codigo}/`
- **JWT Token**: `https://tu-app.onrender.com/api/token/`

## 🛠️ Solución de problemas

### Error de build
```bash
# Limpiar cache de Docker
docker builder prune -a

# Construir sin cache
docker build --no-cache -t pharma-app .
```

### Logs del contenedor
```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Ver logs específicos
docker logs CONTAINER_ID
```

### Problemas de base de datos
```bash
# Verificar conexión
docker-compose exec web python manage.py check --database default

# Recrear base de datos
docker-compose down -v
docker-compose up -d
```

### Archivos estáticos no cargan
Los archivos estáticos se manejan automáticamente por Django en el contenedor. Si tienes problemas, verifica que `collectstatic` se ejecute en el entrypoint.

## 🔄 Actualizaciones

Para actualizar la aplicación en Render:
1. Haz push a tu repositorio GitHub
2. Render rebuildeará automáticamente la imagen
3. La aplicación se reiniciará con la nueva versión

## 📝 Notas adicionales

- El contenedor se ejecuta con un usuario no-root por seguridad
- Los logs se envían a stdout/stderr para que Render los capture
- Health checks están configurados para monitoreo automático
- Los archivos estáticos se sirven directamente desde Django (apropiado para Render)
- CORS está configurado para permitir frontends externos
