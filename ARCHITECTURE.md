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

- La ruta de salida se obtiene de `output.csv_path` en `config.json`. Su valor por defecto es `csv/export.csv`, lo que concentra los CSV de datos en el directorio `csv/` del proyecto. Los usuarios pueden sobreescribir el directorio cambiando `output.csv_path` (por ejemplo `data/export.csv` produce `data/<domain>.csv`).
- Si el directorio de salida no existe, `exporter.py` debe crearlo automáticamente (`Path.mkdir(parents=True, exist_ok=True)`).
- Si el archivo ya existe, será sobrescrito.
- El directorio `csv/` está excluido del repositorio (`.gitignore` contiene `csv/`). Los CSVs se regeneran en cada ejecución y no se versionan.

**Motivación:**
Mantener un comportamiento simple, determinista y predecible, evitando generar nombres de archivo automáticamente o introducir lógica innecesaria. Concentrar los CSVs en un único directorio (`csv/`) reduce el riesgo de borrar accidentalmente archivos Python al manipular resultados y hace explícita la separación entre código y datos.

**Consecuencias:**
- Cada ejecución produce exactamente un archivo en la ruta configurada.
- El usuario controla el nombre y la ubicación del archivo mediante `config.json`; por defecto los archivos quedan en `csv/`.
- La implementación de `exporter.py` encapsula completamente la interacción con el sistema de archivos.
- `output.csv_path` deja de ser un campo obligatorio en `config.json`: si está ausente, se usa el default `csv/export.csv`. Esto reduce friccion al adoptar el proyecto.

---

### ADR-13 — Módulo de comparación entre sitios

**Estado:** Aprobada

**Decisión:**
- Añadir el módulo `compare.py` como **post-procesamiento independiente**.
- Función pública única:

  ```python
  compare_csvs(
      site_a_path: Path,
      site_b_path: Path,
      output_path: Path,
      label_a: str = "nica",
      label_b: str = "lpc",
  ) -> Path
  ```

- CLI delgado:

  ```bash
  python compare.py --site-a A.csv --site-b B.csv [--output csv/comparison.csv]
  ```

- Por convencion, los archivos de entrada se localizan en `csv/` y la salida se guarda en `csv/comparison.csv` por defecto. `--site-a` y `--site-b` siguen siendo obligatorios (el comparador no presupone nombres de archivo concretos). El usuario puede pasar rutas absolutas o relativas a cualquier ubicacion.
- El módulo **no** importa ningún otro módulo del proyecto ni accede a credenciales, red o la API de Google. Su entrada son dos CSVs ya producidos por `download.py`; su salida es un único CSV agregado por consulta.
- Los modelos del dominio (`Config`, `ExecutionRequest`, `SearchResult`) no se modifican ni se extienden.
- `compare.py` no se registra como entry point en `pyproject.toml` (ADR-05: se invoca como `python compare.py`).
- Las columnas de salida, en este orden fijo, son:

  - `query`
  - `{label_a}_clicks`, `{label_a}_impressions`, `{label_a}_ctr`, `{label_a}_position`
  - `{label_b}_clicks`, `{label_b}_impressions`, `{label_b}_ctr`, `{label_b}_position`
  - `status`

- Codificación UTF-8, separador `,`, encabezado en la primera fila. Si el directorio de `output_path` no existe, se crea. Si el archivo existe, se sobrescribe.
- El orden de las filas es alfabético estable por `query`.
- La métrica `position` se pondera por impresiones: `Σ(position × impressions) / Σ(impressions)`. El `ctr` se recalcula como `clicks_total / impressions_total` en lugar de copiarse del CSV de entrada.
- Validaciones de entrada (fail fast):
  - `label_a` y `label_b` deben ser no vacías y distintas entre sí.
  - Ambos CSV de entrada deben existir y contener las columnas `query`, `page`, `clicks`, `impressions`, `ctr`, `position`.
  - `output_path` no puede coincidir con `site_a_path` ni con `site_b_path`. La comparación se hace sobre rutas normalizadas con `Path.resolve()`, lo que cubre rutas relativas/absolutas, segmentos `..` y symlinks.
  - `clicks`, `impressions` y `position` deben ser numéricos y finitos. `nan`, `inf` y `-inf` se rechazan con un mensaje que identifica archivo, fila, consulta y campo.
- Valores `status` posibles: `shared`, `only_{label_a}`, `only_{label_b}`. Con los valores por defecto, los literales son `shared`, `only_nica`, `only_lpc`.

**Motivación:**
La API de Search Analytics es por propiedad; no admite consultar dos sitios en una sola llamada HTTP. `download.py` está modelado en torno a un único `Config.site_url` (ADR-08). Para responder a la pregunta "¿qué términos de búsqueda generaron más impresiones y clics en dos propiedades simultáneamente?" se requiere un paso de post-procesamiento que una los resultados ya descargados. Se elige un módulo independiente en lugar de extender `Config` o `ExecutionRequest` porque (a) la API no lo soporta, (b) mantener `Config` con un único `site_url` simplifica el contrato de descarga, y (c) `compare.py` no necesita ninguno de los modelos existentes.

**Consecuencias:**
- El flujo de comparación requiere dos ejecuciones previas de `download.py` (una por sitio), identificadas por la variable de entorno `GSC_SITE_URL` (ADR-11).
- `Config`, `ExecutionRequest`, `SearchResult`, `exporter.py`, `search_console.py` y `download.py` no se modifican. `compare.py` es un módulo autónomo sin dependencias internas del proyecto.
- El formato del CSV de salida es estable: la columna `status` usa los literales `shared` y `only_<label>`, derivados de las etiquetas configurables. Un cambio en el contrato público (firma, columnas, valores de `status`) requiere una nueva ADR.
- Si en el futuro se quisiera comparar más de dos sitios o recibir un solo CSV de varios dominios, será un módulo nuevo (por ejemplo `compare_many.py`) que reutilice la lógica de agregación; `compare.py` no se extenderá para cubrir ese caso.
