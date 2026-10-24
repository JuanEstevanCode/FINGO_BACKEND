# FINGO Backend

API REST para la aplicación financiera FINGO, construida con FastAPI, Pydantic 2, Psycopg 3 y PostgreSQL. El código del repositorio implementa autenticación, categorías, movimientos y presupuestos. La base de datos debe existir y contar con el esquema compatible: este repositorio no contiene migraciones ni DDL.

## Tecnologías

- Python (versión mínima no fijada en el repositorio), FastAPI y Uvicorn.
- Pydantic 2 para validación de solicitudes y respuestas.
- PostgreSQL mediante `psycopg` 3.
- JWT HS256 (`PyJWT`) y hash de contraseñas mediante `pwdlib` (algoritmo recomendado por la biblioteca).
- `python-dotenv` para cargar configuración local desde `.env`.

Las versiones exactas de paquetes están en [requirements.txt](../requirements.txt).

## Estructura

```text
app/
  main.py                 aplicación y registro de routers; GET /
  database/connection.py  conexión PostgreSQL
  auth/                   registro, login, JWT y dependencia Bearer
  movements/              movimientos y validación de categorías
  categories/             categorías predeterminadas/personales
  budgets/                presupuestos y cálculos agregados
```

No se encontraron pruebas, migraciones, DDL, Dockerfile ni configuración de despliegue versionada.

## Documentación

- [Arquitectura](arquitectura.md)
- [Base de datos](base_de_datos.md)
- [Endpoints](endpoints.md)
- [Autenticación](autenticacion.md)
- [Integración Flutter](integracion_flutter.md)
- [Seguridad y despliegue](seguridad_y_despliegue.md)
- [Pruebas](pruebas.md)

## Arranque local

1. Instala las dependencias de `requirements.txt` en un entorno virtual.
2. Configura las variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `JWT_SECRET_KEY` en el entorno o en `.env` (no compartas el archivo).
3. Prepara PostgreSQL con el esquema esperado descrito en [base_de_datos.md](base_de_datos.md).
4. Ejecuta `uvicorn app.main:app --reload` desde la raíz.
5. Comprueba `GET /` y consulta `/docs` en el host local para OpenAPI.

No existe URL de producción configurada o verificable en este repositorio.

## Backend desplegado

URL base informada: [https://fingo-backend-eag1.onrender.com](https://fingo-backend-eag1.onrender.com). Consulta [endpoints.md](endpoints.md) para las rutas disponibles. La disponibilidad actual del host no fue confirmada durante la edici?nn.
