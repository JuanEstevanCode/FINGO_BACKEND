# Seguridad y despliegue

## Configuración

`app/database/connection.py` lee estas variables para cada conexión: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. `app/auth/security.py` requiere `JWT_SECRET_KEY`; el algoritmo es HS256 y el token dura 30 minutos. `python-dotenv` carga `.env`; `.gitignore` excluye `.env` y `.venv/`.

No se incluyen valores de secretos. Usa un secreto aleatorio robusto y único por entorno, gestión de secretos del proveedor y permisos mínimos para el usuario de BD. No subas `.env`, tokens ni dumps con datos personales.

## Ejecución local

Crea un entorno virtual, instala `pip install -r requirements.txt`, configura las variables anteriores y ejecuta `uvicorn app.main:app --reload`. El esquema PostgreSQL compatible debe aprovisionarse por separado; este repo no trae DDL. La conexión se abre por operación y no implementa pool ni configuración TLS explícita en el código.

## URL desplegada

URL base informada: [https://fingo-backend-eag1.onrender.com](https://fingo-backend-eag1.onrender.com). Config?rala como `API_BASE_URL` en Flutter y utiliza HTTPS. La disponibilidad actual no fue confirmada. El repositorio no incluye manifiestos ni configuraci?n del proveedor para verificar variables, base de datos, escalado o pol?ticas operativas.

## Despliegue seguro

- Ejecutar Uvicorn detrás de un proxy/ingress con TLS; publicar solo HTTPS y configurar correctamente proxy/firewall.
- Usar secretos del entorno, rotación planificada de `JWT_SECRET_KEY` y credenciales DB separadas entre entornos.
- Restringir acceso de red a PostgreSQL y permisos del usuario de aplicación.
- Aplicar esquema/migraciones revisados fuera de este repositorio; validar constraints requeridos para unicidad y exclusión de períodos.
- Configurar CORS si se consume desde Flutter Web. No se observa middleware CORS en la aplicación.
- Añadir gestión de logs sin contraseñas/tokens/datos financieros innecesarios, monitoreo, límites de solicitudes, backups cifrados y restauración verificada según el entorno operativo.
- Desactivar `--reload` en producción. No se encontró Dockerfile, manifiesto de despliegue, URL pública ni configuración de health check.

## Datos personales

Se procesan nombre, correo, fecha de nacimiento y datos de movimientos financieros. Aplicar minimización, control de acceso, retención y obligaciones legales del entorno; no se puede inferir cumplimiento normativo solo del código.
