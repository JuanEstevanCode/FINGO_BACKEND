# Autenticación

## Registro

`POST /auth/registro` valida nombre (2–100), correo con formato Email, fecha de nacimiento y contraseña (8–128). El servicio genera el hash con `pwdlib.PasswordHash.recommended()` y guarda `password_hash`; no conserva la contraseña original. El correo se inserta con `LOWER(%s)`. Un correo duplicado produce `409`. El registro no devuelve token; el cliente inicia sesión después.

## Login y JWT

`POST /auth/login` busca el correo sin distinguir mayúsculas y verifica la contraseña con el hash almacenado. Si coincide genera JWT firmado con HS256. Claims: `sub` (ID de usuario como texto), `iat` y `exp`. La expiración está fijada en 30 minutos. La respuesta entrega `access_token` y `token_type: "bearer"`.

El secreto de firma se lee de `JWT_SECRET_KEY`; la aplicación falla durante la importación si falta. No se documenta aquí ningún valor secreto.

## Rutas protegidas

Se exige el encabezado:

```http
Authorization: Bearer <access_token>
```

`HTTPBearer` y `obtener_usuario_actual` rechazan ausencia, esquema incorrecto, JWT inválido/expirado o `sub` que no sea dígito, con `401` y desafío Bearer. El ID extraído se utiliza para limitar consultas y cambios a recursos del usuario. Categorías predeterminadas son compartidas; categorías personales solo son accesibles por su dueño.

## Sesiones y límites implementados

La API es stateless: no almacena sesión de servidor, no tiene refresh token, revocación, logout, lista de tokens ni endpoint de renovación. El token deja de aceptarse al expirar; cambiar el secreto invalida tokens firmados con el anterior. La app Flutter debe tratar el token como credencial y volver a pedir login al recibir `401`.

Almacenamiento móvil: usar almacenamiento seguro del sistema, como `flutter_secure_storage`; no guardar el JWT en preferencias sin cifrar ni registrarlo en logs. En transporte desplegado usar HTTPS. Estos son pasos de integración recomendados, no características añadidas al backend.
