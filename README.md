
API REST desarrollada con **FastAPI** que integra datos locales con APIs externas

## 📋 Descripción


✅ **Modelado de Datos**: Implementado con SQLAlchemy (Usuario)  
✅ **Endpoint GET**: Combina datos locales con API externa (JSONPlaceholder)  
✅ **Integración API Externa**: Usando HTTPx con manejo de errores  
✅ **Manejo de Excepciones**: Excepciones personalizadas y logging  
✅ **Pruebas Unitarias**: Pytest con coverage  
✅ **Envío de Correos**: Notificaciones basadas en estado externo  
✅ **Dockerización**: Dockerfile y docker-compose.yml  

## 🎯 Endpoint Principal

**`GET /api/v1/usuarios/{id}/con-datos-externos`**

Este endpoint cumple con el requisito principal de la prueba técnica:
1. Consulta un usuario en la base de datos local
2. Obtiene datos adicionales de JSONPlaceholder API
3. Combina ambos datos en una respuesta JSON
4. Envía correo si el usuario está inactivo externamente

### Ejemplo de Respuesta

```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "activo": true,
  "fecha_creacion": "2024-01-01T10:00:00Z",
  "datos_externos": {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
      "name": "Romaguera-Crona",
      "catchPhrase": "Multi-layered client-server neural-net"
    }
  }
}
```

## 🏗️ Arquitectura

```
├── app/
│   ├── api/
│   │   ├── endpoints/        # Endpoints por recurso
│   │   │   ├── usuarios.py   # 🎯 Endpoint principal aquí
│   │   │   ├── productos.py
│   │   │   ├── pedidos.py
│   │   │   └── health.py
│   │   └── router.py         # Router principal
│   ├── services/
│   │   ├── external_api_service.py  # Integración API externa
│   │   ├── email_service.py         # Envío de correos
│   │   └── database_service.py      # CRUD operations
│   ├── models.py             # Modelos SQLAlchemy
│   ├── schemas.py            # Esquemas Pydantic
│   ├── database.py           # Configuración DB
│   ├── config.py             # Configuración
│   └── exceptions.py         # Excepciones personalizadas
├── tests/                    # Pruebas unitarias
├── app/main.py              # Punto de entrada de la aplicación
├── Dockerfile               # Containerización
└── docker-compose.yml       # Orquestación
```

## 🛠️ Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/NicolasHurtado/FastAPI_external_api.git
cd FastAPI_external_api

# Levantar con Docker Compose
docker-compose up --build

# La API estará disponible en http://localhost:8000
# El usuario de prueba se crea automáticamente
```

**Flujo de Inicialización con Docker:**
1. 🐘 PostgreSQL se inicia y espera estar healthy
2. 🚀 FastAPI se inicia y crea las tablas
3. 👤 Script de inicialización crea el usuario de prueba
4. ✅ Sistema listo para usar

### Opción 2: Instalación Local con Poetry

```bash
# Instalar Poetry (si no lo tienes)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias del proyecto
poetry install

# Configurar base de datos PostgreSQL
# Copiar configuración de ejemplo
cp .env.template .env

# Editar .env con tus credenciales
DATABASE_URL=postgresql://user:password@localhost:5432/test_db
```

### Opción 3: Instalación Local con pip (alternativa)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
# Copiar configuración de ejemplo
cp .env.template .env

# Editar .env con tus credenciales
DATABASE_URL=postgresql://user:password@localhost:5432/test_db

# Ejecutar la aplicación
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🗄️ Base de Datos

### Modelos Implementados

#### 👤 Usuario
- `id`: Primary key
- `nombre`: Nombre completo
- `email`: Email único
- `activo`: Estado del usuario
- `fecha_creacion/actualizacion`: Timestamps


### Inicialización de Base de Datos

**Tablas**: Se crean **automáticamente** al arrancar la aplicación FastAPI.

**Datos de Prueba**: Se crea un usuario inicial con el script de inicialización:
- **Email**: `admin@test.com`
- **Nombre**: `Usuario de Prueba`
- **Estado**: `Activo`

Para crear datos adicionales, puedes usar los endpoints POST disponibles en la API REST.

## 🔌 API Externa Integrada

**JSONPlaceholder** (`https://jsonplaceholder.typicode.com`)

- **Usuarios**: `/users/{id}` - Datos de perfil interno
- **con-datos-externos**: `/users/{id}/con-datos-externos` - Datos de perfil externo

### Manejo de Errores

- ✅ Timeout configurable
- ✅ Retry logic implícito
- ✅ Fallback a datos locales
- ✅ Logging detallado
- ✅ Excepciones específicas

## 📧 Sistema de Correos

Envío automático de notificaciones cuando:
- Usuario tiene estado "inactive" en API externa
- Configuración SMTP opcional
- Templates HTML y texto plano

### Configuración

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
```

## 🧪 Pruebas Unitarias

### Con Poetry (Recomendado)

```bash
# Ejecutar todas las pruebas
docker-compose exec app poetry run pytest -v


# Pruebas específicas
docker-compose exec app poetry run pytest tests/test_endpoints.py -v
docker-compose exec app poetry run pytest tests/test_database_service.py -v
docker-compose exec app poetry run pytest tests/test_external_api_service.py -v

```

### Con pip

```bash
# Ejecutar todas las pruebas
pytest

# Pruebas específicas
pytest tests/test_endpoints.py -v
pytest tests/test_database_service.py -v
pytest tests/test_external_api_service.py -v
```

### Cobertura de Pruebas

- ✅ Servicios CRUD completos
- ✅ Integración API externa
- ✅ Endpoints principales
- ✅ Manejo de excepciones
- ✅ Mocking de servicios externos

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:password@localhost:5432/test_db` |
| `EXTERNAL_API_BASE_URL` | URL base API externa | `https://jsonplaceholder.typicode.com` |
| `EXTERNAL_API_TIMEOUT` | Timeout en segundos | `30` |
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8000` |
| `DEBUG` | Modo debug | `true` |
| `SMTP_*` | Configuración email | Opcional |

## 📊 Endpoints Disponibles

### 🎯 Endpoint Principal (Prueba Técnica)
- `GET /api/v1/usuarios/{id}/con-datos-externos` - Combina datos locales y externos

### 👥 Usuarios
- `GET /api/v1/usuarios/` - Lista usuarios
- `POST /api/v1/usuarios/` - Crear usuario
- `GET /api/v1/usuarios/{id}` - Obtener usuario
- `PUT /api/v1/usuarios/{id}` - Actualizar usuario
- `DELETE /api/v1/usuarios/{id}` - Eliminar usuari

### 🏥 Health Check
- `GET /api/v1/health/` - Estado básico
- `GET /api/v1/health/detailed` - Estado detallado con componentes

## 📖 Documentación API

Una vez ejecutando la aplicación:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🚀 Ejemplos de Uso

### Probar el Endpoint Principal

```bash
# Crear un usuario
curl -X POST "http://localhost:8000/api/v1/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan.perez@example.com",
    "activo": true
  }'

# Obtener usuario con datos externos (🎯 ENDPOINT PRINCIPAL)
curl "http://localhost:8000/api/v1/usuarios/1/con-datos-externos"
```

### Verificar Health Check

```bash
# Health básico
curl "http://localhost:8000/api/v1/health/"

# Health detallado
curl "http://localhost:8000/api/v1/health/detailed"
```

## 📦 Gestión de Dependencias con Poetry

Este proyecto utiliza **Poetry** para la gestión moderna de dependencias de Python. Poetry ofrece:

### ✅ **Ventajas de Poetry**
- **Gestión determinística** de dependencias con `poetry.lock`
- **Separación clara** entre dependencias de producción y desarrollo
- **Resolución automática** de conflictos de versiones
- **Construcción y publicación** de paquetes simplificada
- **Entornos virtuales** automáticos y aislados


### 📋 **Scripts Predefinidos**

En `pyproject.toml` se han definido scripts útiles:

```toml
[tool.poetry.scripts]
start-server = "app.main:start_server"
```

### 🔧 **Herramientas de Desarrollo Incluidas**

- **pytest**: Framework de pruebas con coverage
- **black**: Formateador de código automático
- **isort**: Organizador de imports
- **flake8**: Linter para calidad de código
- **mypy**: Verificador de tipos estáticos

```bash
# Formatear código
docker-compose exec app poetry run black app/ tests/

# Organizar imports
docker-compose exec app poetry run isort app/ tests/

# Verificar linting
docker-compose exec app poetry run flake8 app/ tests/

# Verificar tipos
docker-compose exec app poetry run mypy app/
```

## 🏆 Mejores Prácticas Implementadas

### 🔧 Arquitectura
- ✅ Clean Architecture con separación de responsabilidades
- ✅ Dependency Injection con FastAPI
- ✅ Repository pattern para base de datos
- ✅ Service layer para lógica de negocio

### 🛡️ Seguridad
- ✅ Validación de entrada con Pydantic
- ✅ Manejo seguro de excepciones
- ✅ Logging sin información sensible
- ✅ Usuario no root en Docker

### 📊 Monitoreo
- ✅ Health checks comprehensivos
- ✅ Logging estructurado
- ✅ Métricas de rendimiento
- ✅ Manejo de errores detallado

### 🧪 Testing
- ✅ Tests unitarios con pytest
- ✅ Mocking de servicios externos
- ✅ Test database separada
- ✅ Fixtures reutilizables

## 🔄 Flujo de Trabajo

1. **Solicitud HTTP** → FastAPI Router
2. **Validación** → Pydantic Schemas
3. **Lógica de Negocio** → Service Layer
4. **Base de Datos** → SQLAlchemy ORM
5. **API Externa** → HTTPx Client
6. **Respuesta** → JSON serializado

## 📝 Notas Técnicas

### Decisiones de Arquitectura

- **FastAPI**: Framework moderno con validación automática
- **SQLAlchemy**: ORM robusto con soporte async
- **HTTPx**: Cliente HTTP async para mejor performance
- **Pydantic**: Validación de datos y serialización
- **PostgreSQL**: Base de datos relacional confiable
- **Poetry**: Gestión moderna de dependencias y proyectos Python

### Manejo de Errores

- Excepciones personalizadas por tipo de error
- Logging detallado para debugging
- Respuestas HTTP consistentes
- Graceful degradation en APIs externas

### Performance

- Conexiones async a APIs externas
- Pool de conexiones de base de datos
- Caching de configuración
- Logging eficiente

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request


## 📞 Contact

For any inquiries about the project, contact us at [nicolashurtado0712@gmail.com](mailto:nicolashurtado0712@gmail.com).

---

Developed with ❤️ by Nicolas Hurtado
