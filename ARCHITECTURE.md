# Arquitectura del Proyecto — Google Search Console Export

## v1 — Versión inicial

### Objetivo funcional

Script local en Python (`python download.py`) que:
1. Autentica al usuario mediante OAuth 2.0 (Installed Application Flow).
2. Consulta `searchanalytics.query` con dimensiones `query` y `page`.
3. Exporta los resultados a un CSV con las columnas: `query`, `page`, `clicks`, `impressions`, `ctr`, `position`.

---

### Autenticación

**Decisión:** OAuth 2.0 Installed Application Flow.

**Bibliotecas:**
- `google-api-python-client`
- `google-auth-library-python`
- `google-auth-oauthlib` (`InstalledAppFlow`)

**Scope:** `https://www.googleapis.com/auth/webmasters.readonly`

---

### Configuración estable (config.json)

`config.json` contiene únicamente información estable que no cambia entre ejecuciones:

- Autenticación (rutas a `client_secrets.json` y al almacén de tokens).
- Propiedad de Search Console (`site_url`).
- Configuración de salida (`csv_path`).
- Opciones permanentes de consulta (`type`, `row_limit`, `dimensions`).

**No almacena fechas.**

---

### Contrato de configuración (config.json)

```json
{
  "auth": {
    "client_secrets_path": "client_secrets.json",
    "token_store_path": ".token_cache.json"
  },
  "gsc": {
    "site_url": "https://www.example.com/"
  },
  "query": {
    "dimensions": ["query", "page"],
    "type": "web",
    "row_limit": 1000
  },
  "output": {
    "csv_path": "export.csv"
  }
}
```

**Campos imprescindible para v1:**
- `auth.client_secrets_path`
- `gsc.site_url`
- `output.csv_path`

`query.start_date` y `query.end_date` **no existen en config.json**: se proporcionan como argumentos de línea de comandos (`--last N`, `--start YYYY-MM-DD`, `--end YYYY-MM-DD`).

---

### Notas de la v1

- Solo se consultan las dimensiones `query` y `page` (sin filtros avanzados ni paginación manual).
- `row_limit` por defecto de la API es 1,000; se deja configurable para permitir al usuario aumentarlo.
- La agregación usa el valor por defecto (`auto`); `aggregationType` se prepara en el schema para futuras versiones.

---

## Decisiones de arquitectura aprobadas

| # | Decisión | Fecha |
|---|----------|-------|
| 1 | OAuth 2.0 Installed Application Flow como método de autenticación. | 2026-07-28 |
| 2 | `PROJECT_CONTEXT.md` es la referencia técnica basada en documentación oficial. `ARCHITECTURE.md` contiene únicamente decisiones propias del proyecto. | 2026-07-28 |
| 3 | Las fechas (`start_date`, `end_date`) son parámetros de ejecución, no campos de `config.json`. Flujo principal: `python download.py --last 30`. | 2026-07-28 |
| 4 | `config.json` almacena exclusivamente información estable: autenticación, `site_url`, salida y opciones permanentes de consulta. | 2026-07-28 |

---

## Registro de Decisiones de Arquitectura (ADR)

### ADR-05 — Filosofía del proyecto

**Estado:** Aprobada

**Decisión:**
- La solución más simple que resuelva correctamente el problema.
- "Menos es más".
- No se añadirán abstracciones, archivos, clases o patrones "por si acaso".
- Toda nueva abstracción debe justificar claramente su existencia en la versión actual del proyecto.

**Motivación:**
Evitar sobreingeniería y mantener el proyecto fácil de mantener y entender. Cada elemento debe tener un propósito claro y demostrado, no hipotético.

**Consecuencias:**
- Se rechaza código que añada complejidad sin beneficios tangibles inmediatos.
- Las decisiones de abstracción se toman en el momento en que la necesidad es real, no anticipada.
- El código puede requerir refactorizaciones futuras si el proyecto crece, pero se aceptan como parte de la evolución natural.

---

### ADR-06 — Estructura del proyecto

**Estado:** Aprobada

**Decisión:**
El proyecto se estructura en los siguientes módulos con responsabilidades claras:

| Módulo | Responsabilidad |
|--------|-----------------|
| `download.py` | Punto de entrada de la aplicación y orquestador del flujo de ejecución. No contiene lógica de negocio. |
| `config.py` | Carga y validación de la configuración. |
| `auth.py` | Autenticación OAuth. |
| `search_console.py` | Comunicación con la Search Analytics API. |
| `exporter.py` | Exportación a CSV. |
| `models.py` | Modelos del dominio. |

**Motivación:**
Separación de responsabilidades que permite modificar cada área de forma independiente. Cada módulo tiene una única razón para cambiar.

**Consecuencias:**
- Cada módulo es reemplazable sin afectar a los demás.
- Se facilita la escritura de pruebas unitarias.
- La estructura es plana y fácil de navegar.

---

### ADR-07 — Comunicación entre módulos

**Estado:** Aprobada

**Decisión:**
- Los módulos intercambian exclusivamente modelos del dominio (`Config`, `ExecutionRequest` y `SearchResult`) y tipos externos cuando sea necesario (por ejemplo `Credentials` y `Path`).
- Ningún módulo lee archivos gestionados por otro módulo.
- `download.py` es el único módulo que conoce a todos los demás.
- Los demás módulos no dependen entre sí.

**Motivación:**
Minimizar el acoplamiento y maximizar la cohesión. Un módulo bien definido no necesita conocer cómo funcionan los demás, solo la interfaz que consume.

**Consecuencias:**
- `download.py` actúa como pegamento entre los módulos.
- Los datos fluyen como objetos inmutables o estructurados entre funciones.
- Cambiar la implementación de un módulo no requiere cambios en otros.

---

### ADR-08 — Modelos del dominio

**Estado:** Aprobada

**Decisión:**
Los modelos del dominio se definen como dataclasses dentro de `models.py`:

| Modelo | Descripción |
|--------|-------------|
| `Config` | Configuración cargada y validada del proyecto. |
| `ExecutionRequest` | Solicitud de ejecución con parámetros de fecha y consulta. |
| `SearchResult` | Resultado individual de Search Analytics representado con campos del dominio. |

Los modelos del dominio no contienen lógica de negocio. Su única responsabilidad es representar datos del dominio.

`SearchResult` representa el dominio del proyecto y no la estructura interna de la respuesta de Google Search Console. La transformación desde la respuesta de la API hacia el modelo del dominio es responsabilidad exclusiva de `search_console.py`.

**Motivación:**
El dominio del proyecto no debe quedar acoplado al formato de una API externa. Representar los datos con campos explícitos del negocio (`query`, `page`) en lugar de la estructura interna de la API (`keys`) mantiene el modelo limpio y preparado para futuras transformaciones.

**Consecuencias:**
- Los modelos son la única fuente de verdad para los datos del dominio.
- Facilita la validación y transformación de datos.
- Cada modelo es serializable si es necesario en el futuro.
- La transformación de `keys` a campos del dominio ocurre en `search_console.py`.

---

### ADR-09 — Interfaces públicas

**Estado:** Aprobada

**Decisión:**
Cada módulo expone una interfaz pública mínima y clara:

**config.py**
```python
load_config() -> Config
```

**auth.py**
```python
authenticate(
    config: Config,
) -> Credentials
```

**search_console.py**
```python
download_search_analytics(
    credentials: Credentials,
    config: Config,
    request: ExecutionRequest,
) -> list[SearchResult]
```

**exporter.py**
```python
export_csv(
    rows: list[SearchResult],
    config: Config,
) -> Path
```

`download.py` no expone API pública; únicamente actúa como punto de entrada de la aplicación.

**Motivación:**
Interfaces pequeñas y enfocadas facilitan el uso correcto y reducen la superficie de contacto entre módulos.

**Consecuencias:**
- Los consumidores saben exactamente qué necesitan y qué obtendrán.
- La implementación interna puede cambiar sin afectar a los consumidores.
- Documentar las interfaces es trivial.

---

### ADR-10 — Flujo de ejecución

**Estado:** Aprobada

**Decisión:**
El flujo de ejecución sigue esta secuencia:

1. Leer argumentos CLI.
2. Cargar configuración.
3. Validar configuración.
4. Autenticar con Google.
5. Construir ExecutionRequest.
6. Descargar Search Analytics.
7. Exportar CSV.
8. Mostrar un resumen de la ejecución.
9. Finalizar.

**Motivación:**
Flujo lineal y predecible que facilita el debugging y la comprensión del programa.

**Consecuencias:**
- Cada paso es ejecutable de forma independiente en teoría.
- Errores en pasos tempranos impiden la ejecución de pasos posteriores.
- El resumen final proporciona feedback claro al usuario.

---

### ADR-11 — Contrato de la CLI

**Estado:** Aprobada

**Decisión:**
**Flujo principal:**
```
python download.py --last <N>
```

**Diseño preparado para soportar:**
```
python download.py --start YYYY-MM-DD --end YYYY-MM-DD
```

**Reglas:**
- Debe utilizarse exactamente una modalidad de fechas.
- `--last` es incompatible con `--start/--end`.
- `--start` requiere `--end`.
- `--end` requiere `--start`.

**Semántica de `--last N`:**
- `--last N` representa exactamente N dias naturales, incluyendo la fecha final.
- El rango se calcula como: `end_date = hoy`, `start_date = hoy - (N - 1)`.
- Ejemplos: `--last 1` devuelve solo hoy; `--last 7` devuelve los ultimos 7 dias incluyendo hoy.
- N debe ser un entero positivo (N >= 1).

**Motivación:**
Interfaz simple que cubre el caso de uso más común (últimos N días) con diseño preparado para escenarios futuros sin añadir complejidad innecesaria.

**Consecuencias:**
- El usuario no puede combinar ambas modalidades.
- La validación de argumentos es clara y mensajes de error son descriptivos.
- Extender a nuevas modalidades en el futuro no requiere cambiar la estructura actual.

---

### ADR-12 — Contrato de exportación CSV

**Estado:** Aprobada

**Decisión:**
- El formato de salida es CSV.
- Codificación UTF-8.
- Separador ",".
- La primera fila contiene los encabezados.
- El orden de las columnas es fijo:

  - `query`
  - `page`
  - `clicks`
  - `impressions`
  - `ctr`
  - `position`

- La ruta de salida se obtiene de `output.csv_path` en `config.json`.
- Si el directorio de salida no existe, `exporter.py` debe crearlo automáticamente.
- Si el archivo ya existe, será sobrescrito.

**Motivación:**
Mantener un comportamiento simple, determinista y predecible, evitando generar nombres de archivo automáticamente o introducir lógica innecesaria.

**Consecuencias:**
- Cada ejecución produce exactamente un archivo en la ruta configurada.
- El usuario controla el nombre y la ubicación del archivo mediante `config.json`.
- La implementación de `exporter.py` encapsula completamente la interacción con el sistema de archivos.
