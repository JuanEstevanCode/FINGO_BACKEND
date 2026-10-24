# Integración Flutter

Gu?a de consumo HTTP de las rutas existentes. Para el backend desplegado configura `https://fingo-backend-eag1.onrender.com` como `API_BASE_URL` sin barra final y agrega la ruta del endpoint.

## 1. URL base según entorno

- Android Emulator: `http://10.0.2.2:8000` accede al host de desarrollo; `localhost` dentro del emulador apunta al propio emulador.
- Simulador iOS: normalmente `http://127.0.0.1:8000` según configuración local.
- Teléfono físico: `http://<IP-LAN-del-equipo>:8000`; teléfono y equipo deben compartir red y el firewall debe permitir el puerto. Arranca Uvicorn escuchando en la interfaz necesaria, por ejemplo `--host 0.0.0.0` solo en una red de desarrollo confiable.
- Desplegado: usa `https://fingo-backend-eag1.onrender.com` como `API_BASE_URL` y agrega la ruta, por ejemplo `/auth/login`.
La URL desplegada usa HTTPS. El backend no configura CORS. CORS afecta clientes web Flutter; apps nativas no aplican la pol?tica CORS del navegador. Para Flutter Web se debe configurar CORS en el servidor. Las restricciones HTTP en Android/iOS dependen de la configuraci?n de plataforma.

## 2. Dependencias sugeridas

Añade `http` y `flutter_secure_storage` al `pubspec.yaml` de la app Flutter. Ajusta versiones a las compatibles con tu proyecto. Define URL por flavor/`--dart-define`, sin incluir secretos:

```dart
const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://fingo-backend-eag1.onrender.com',
);
```

Para teléfono físico ejecuta con, por ejemplo, `--dart-define=API_BASE_URL=http://192.168.1.20:8000`; para despliegue usa el HTTPS real provisto por el operador.

## 3. Cliente HTTP, token y errores

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  ApiClient(this.baseUrl);
  final String baseUrl;
  final _storage = const FlutterSecureStorage();
  String? _token;

  Future<void> guardarToken(String token) async {
    _token = token;
    await _storage.write(key: 'fingo_access_token', value: token);
  }

  Future<void> cargarToken() async {
    _token = await _storage.read(key: 'fingo_access_token');
  }

  Future<void> cerrarSesionLocal() async {
    _token = null;
    await _storage.delete(key: 'fingo_access_token');
    // El backend no ofrece logout/revocación.
  }

  Future<http.Response> request(
    String method,
    String path, {
    Map<String, String>? query,
    Object? body,
    bool autenticado = true,
  }) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    final headers = <String, String>{'Accept': 'application/json'};
    if (body != null) headers['Content-Type'] = 'application/json';
    if (autenticado && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    final payload = body == null ? null : jsonEncode(body);
    switch (method) {
      case 'GET': return http.get(uri, headers: headers);
      case 'POST': return http.post(uri, headers: headers, body: payload);
      case 'PUT': return http.put(uri, headers: headers, body: payload);
      case 'PATCH': return http.patch(uri, headers: headers, body: payload);
      case 'DELETE': return http.delete(uri, headers: headers);
      default: throw ArgumentError('Método no soportado: $method');
    }
  }

  dynamic decodificar(http.Response r) {
    if (r.statusCode == 204 || r.body.isEmpty) return null;
    final data = jsonDecode(r.body);
    if (r.statusCode < 200 || r.statusCode >= 300) {
      final detail = data is Map ? data['detail'] : null;
      throw Exception('HTTP ${r.statusCode}: $detail');
    }
    return data;
  }
}
```

Maneja `401` limpiando el token y solicitando nuevo login; `422` suele señalar entrada inválida y FastAPI puede devolver una lista de errores en `detail`; `404` recurso no disponible; `409` conflicto. Trata fallos de red/timeout aparte de respuestas HTTP. Evita imprimir contraseña, cuerpo de login o token.

## 4. Login y modelos básicos

```dart
Future<void> login(ApiClient api, String correo, String password) async {
  final r = await api.request('POST', '/auth/login', autenticado: false,
      body: {'correo': correo, 'password': password});
  final data = api.decodificar(r) as Map<String, dynamic>;
  await api.guardarToken(data['access_token'] as String);
}

class Movimiento {
  final String tipo;
  final String monto;
  final int categoriaId;
  final String? descripcion;
  final String fecha;
  const Movimiento(this.tipo, this.monto, this.categoriaId, this.fecha,
      {this.descripcion});
  Map<String, dynamic> toJson() => {
    'tipo': tipo, 'monto': monto, 'categoria_id': categoriaId,
    'descripcion': descripcion, 'fecha': fecha,
  };
}

class Presupuesto {
  final int categoriaId;
  final String tipoPeriodo;
  final String fechaInicio;
  final String fechaFin;
  final String montoLimite;
  const Presupuesto(this.categoriaId, this.tipoPeriodo, this.fechaInicio,
      this.fechaFin, this.montoLimite);
  Map<String, dynamic> toJson() => {
    'categoria_id': categoriaId, 'tipo_periodo': tipoPeriodo,
    'fecha_inicio': fechaInicio, 'fecha_fin': fechaFin,
    'monto_limite': montoLimite,
  };
}
```

Registro usa `POST /auth/registro` con `nombre`, `correo`, `fecha_nacimiento` (`YYYY-MM-DD`) y `password`; la respuesta no contiene token, luego llama a login.

## 5. Categorías y movimientos

```dart
// Categorías visibles (predeterminadas + propias)
final categorias = api.decodificar(await api.request('GET', '/categorias/'));
// Filtrar por tipo
final gastos = api.decodificar(await api.request('GET', '/categorias/',
    query: {'tipo': 'gasto'}));
// Crear categoría personal
final nueva = api.decodificar(await api.request('POST', '/categorias/',
    body: {'nombre': 'Mascotas', 'tipo': 'gasto'}));

// Crear movimiento; categoria_id debe ser una categoría activa del tipo correcto
final creado = api.decodificar(await api.request('POST', '/movimientos/',
    body: Movimiento('gasto', '12500.00', 3, '2026-10-24',
        descripcion: 'Mercado').toJson()));
// Listar con paginación y filtros
final lista = api.decodificar(await api.request('GET', '/movimientos/',
    query: {'tipo': 'gasto', 'limite': '20', 'desplazamiento': '0'}));
// Leer, reemplazar (PUT exige el cuerpo completo) y borrar
final uno = api.decodificar(await api.request('GET', '/movimientos/42'));
await api.request('PUT', '/movimientos/42', body:
    Movimiento('gasto', '13000.00', 3, '2026-10-24').toJson());
api.decodificar(await api.request('DELETE', '/movimientos/42'));
```

Nota: las respuestas de categorías y movimientos son arrays posicionales serializados desde Psycopg, no objetos con claves documentadas por un esquema. Valida la representación observada en la instalación y considera actualizar el backend para modelos de respuesta antes de acoplar modelos Dart rígidos.

Para desactivar una categoría personal: `PATCH /categorias/{id}/desactivar`, sin cuerpo. Para renombrarla: `PUT /categorias/{id}` con `{"nombre":"Nuevo nombre"}`. No se permite editar categorías predeterminadas.

## 6. Presupuestos

```dart
final body = Presupuesto(3, 'mensual', '2026-10-01', '2026-10-31', '500000.00');
final presupuesto = api.decodificar(await api.request('POST', '/presupuestos/',
    body: body.toJson()));
final todos = api.decodificar(await api.request('GET', '/presupuestos/'));
final detalle = api.decodificar(await api.request('GET', '/presupuestos/7'));
final actualizado = api.decodificar(await api.request('PUT', '/presupuestos/7',
    body: body.toJson()));
final borrado = api.decodificar(await api.request('DELETE', '/presupuestos/7'));
```

Un presupuesto mensual debe cubrir exactamente el mes calendario. Para `personalizado`, las fechas solo exigen inicio no posterior al fin. La categoría debe ser activa, accesible y de tipo gasto. El backend calcula acumulado/saldo/estado al leer.

## 7. Lista de comprobación

1. Inicia backend y PostgreSQL con esquema compatible.
2. Comprueba `GET /` desde emulador/dispositivo.
3. Prueba login, conserva el token seguromente y consulta `GET /categorias/`.
4. Crea movimiento con ID de categoría válida y confirma que aparece en el listado.
5. Consulta/crea un presupuesto y revisa su respuesta agregada.
6. Repite con token vencido para verificar flujo `401` y nuevo login.
