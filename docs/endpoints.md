# Endpoints

Base: la URL configurada por el cliente (sin barra final), seguida de la ruta. La API no define prefijo global. Los cuerpos de error de FastAPI suelen ser `{"detail":"..."}`; validación Pydantic responde `422` con `detail` estructurado.

Las respuestas no tipadas de movimientos y categorías se originan en tuplas Psycopg y FastAPI las serializa como arrays posicionales. Para movimientos el orden es `[id, tipo, monto, categoria_id, categoria, descripcion, fecha]`; categoría `[id, nombre, tipo, es_predeterminada, activa]`. Puede variar el formato JSON del decimal según el driver/serializador; no se transforma explícitamente en modelos.

| Método y ruta | Auth | Entrada/salida y respuestas relevantes |
|---|---|---|
| `GET /` | No | Sin entrada. `200 {"message":"FINGO API funcionando"}`. |
| `POST /auth/registro` | No | JSON: `nombre` (2–100), `correo` (Email), `fecha_nacimiento` (`YYYY-MM-DD`), `password` (8–128). `201 {"mensaje":"Usuario registrado satisfactoriamente.","access_token":null,"token_type":null}`. `409` correo existente; `500` error PostgreSQL. |
| `POST /auth/login` | No | JSON: `correo`, `password` (8–128). `200 {"mensaje":"Autenticación satisfactoria.","access_token":"<JWT>","token_type":"bearer"}`. `401` credenciales incorrectas; `500` error PostgreSQL. |
| `GET /categorias/` | Bearer | Query opcional `tipo=ingreso|gasto`. Devuelve lista de filas `[id,nombre,tipo,es_predeterminada,activa]`. `422` tipo inválido. |
| `POST /categorias/` | Bearer | JSON `{"nombre":"...","tipo":"ingreso"|"gasto"}`. `201 {"message":"Categoría creada correctamente.","id":1}`. `409` duplicada. |
| `PUT /categorias/{categoria_id}` | Bearer | JSON `{"nombre":"..."}`. Renombra categoría personal activa. `200 {"message":"Categoría actualizada correctamente.","id":1}`; `404` inaccesible/no personal/inactiva; `409` duplicada. |
| `PATCH /categorias/{categoria_id}/desactivar` | Bearer | Sin cuerpo. Desactivación lógica. `200 {"message":"Categoría desactivada correctamente.","id":1}`; `404` no encontrada/no personal/inactiva. |
| `POST /movimientos/` | Bearer | JSON: `tipo` (`ingreso`/`gasto`), `monto` (>0, máximo 12 dígitos/2 decimales), `categoria_id` (>0), `descripcion` opcional/null (máx. 500), `fecha` (`YYYY-MM-DD`). `201 {"message":"Movimiento registrado correctamente","id":1}`; `422` categoría no válida/inactiva/de otro tipo o entrada inválida. |
| `GET /movimientos/` | Bearer | Query: `tipo` opcional, `categoria_id` opcional (>0), `fecha_desde`, `fecha_hasta` ISO, `limite` 1–100 (default 20), `desplazamiento` ≥0 (default 0). Lista ordenada fecha e ID descendente; cada fila `[id,tipo,monto,categoria_id,categoria,descripcion,fecha]`. `422` rango invertido/tipo inválido. |
| `GET /movimientos/{movement_id}` | Bearer | Sin entrada. Fila `[id,tipo,monto,categoria_id,categoria,descripcion,fecha]`; `404` si no pertenece al usuario o no existe. |
| `PUT /movimientos/{movement_id}` | Bearer | Mismo cuerpo completo que crear. Reemplaza campos editables. `200 {"message":"Movimiento actualizado correctamente","id":1}`; `404` ausente/no propio; `422` validación/categoría. |
| `DELETE /movimientos/{movement_id}` | Bearer | Sin cuerpo. `200 {"message":"Movimiento eliminado correctamente","id":1}`; `404` ausente/no propio. |
| `POST /presupuestos/` | Bearer | JSON: `categoria_id` >0, `tipo_periodo` (`mensual`/`personalizado`), `fecha_inicio`, `fecha_fin`, `monto_limite` positivo (12/2). Mensual exige inicio día 1 y fin último día del mismo mes. `201` objeto `BudgetResponse`; `409` superposición; `422` categoría no válida/gasto o validación. |
| `GET /presupuestos/` | Bearer | Sin parámetros. Lista de `BudgetResponse` del usuario. `200`. |
| `GET /presupuestos/{presupuesto_id}` | Bearer | Objeto `BudgetResponse`; `404` no encontrado/no propio. |
| `PUT /presupuestos/{presupuesto_id}` | Bearer | Mismo cuerpo completo que crear. `200` `BudgetResponse`; `404` si presupuesto o categoría no accesibles; `409` período superpuesto; `422` validación. |
| `DELETE /presupuestos/{presupuesto_id}` | Bearer | Sin cuerpo. `204` sin cuerpo; `404` no encontrado/no propio. |

`BudgetResponse`: `id`, `usuario_id`, `categoria_id`, `categoria_nombre`, `tipo_periodo`, `fecha_inicio`, `fecha_fin`, `monto_limite`, `gasto_acumulado`, `saldo_disponible`, `porcentaje_utilizado`, `estado` (`normal`, `proximo_limite`, `excedido`), `fecha_creacion`. El gasto suma movimientos de tipo gasto de esa categoría y usuario dentro del intervalo, inclusive. Estado pasa a próximo límite desde 80% y excedido cuando supera el monto; exactamente 100% queda `proximo_limite`.

## Ejemplos HTTP

```http
POST /auth/login
Content-Type: application/json

{"correo":"ana@example.com","password":"<contraseña>"}
```

```http
GET /movimientos/?tipo=gasto&limite=20&desplazamiento=0
Authorization: Bearer <JWT>
```

```json
{"tipo":"gasto","monto":"12500.00","categoria_id":3,"descripcion":"Mercado","fecha":"2026-10-24"}
```

El prefijo `/` final está declarado en rutas de colección. FastAPI puede redirigir si se omite; los clientes deben usar las rutas exactamente como se publican.

OpenAPI interactivo: `/docs` en el host donde se ejecute la API.
