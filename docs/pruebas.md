# Pruebas y verificación

## Estado del repositorio

No se encontraron archivos de pruebas (`test_*.py`, `*_test.py`), configuración de pytest, fixtures, CI, colección Postman ni scripts de seed. Por ello no hay suite de pruebas documentada ni un comando de tests verificable. Las pruebas deben agregarse como trabajo separado; esta documentación no las crea ni las ejecuta.

## Verificación manual disponible

Con PostgreSQL preparado con esquema compatible y variables configuradas:

1. `uvicorn app.main:app --reload`
2. `GET /` debe responder `200` con `{"message":"FINGO API funcionando"}`.
3. Desde `/docs`, crear usuario, hacer login y copiar temporalmente el token en un entorno de desarrollo controlado.
4. Usar `Authorization: Bearer <token>` para listar categorías, crear/listar movimiento y crear/listar presupuesto.
5. Confirmar errores: credenciales erróneas `401`, token omitido o expirado `401`, recurso ajeno/inexistente `404`, duplicidad/superposición `409`, datos inválidos `422`.

No usar usuarios, contraseñas ni datos financieros reales en pruebas manuales compartidas. No registrar token en consola o repositorio.

## Comprobación de Flutter

Configura `API_BASE_URL` según [integracion_flutter.md](integracion_flutter.md). Comprueba conectividad antes de depurar modelos; luego valida login, almacenamiento seguro, envío Bearer, operaciones de categorías, movimientos y presupuestos, y manejo de `401`, `404`, `409`, `422`, `204` y fallos de red.

Importante: movimientos y categorías no tienen esquema de respuesta Pydantic y se basan en filas posicionales de Psycopg. Verifica su serialización en la versión instalada o adapta el backend en un cambio posterior antes de fijar contratos Dart fuertes.
## Comprobaci?n del backend desplegado

La URL informada es `https://fingo-backend-eag1.onrender.com`. Comprueba manualmente `GET https://fingo-backend-eag1.onrender.com/`; la respuesta esperada seg?n `app/main.py` es `200` con `{"message":"FINGO API funcionando"}`. La disponibilidad actual no fue confirmada. Si est? habilitada, OpenAPI se encuentra en `https://fingo-backend-eag1.onrender.com/docs`.


## Comprobaci?n de Flutter
