# GSC Export

A lightweight Python CLI to export Google Search Console Search Analytics data to CSV using the official Google Search Console API.
Herramienta de linea de comandos para exportar datos de Google Search Console Search Analytics a CSV.

---

## Caracteristicas

- Autenticacion mediante OAuth2 con Google.
- Consulta datos de Google Search Console Search Analytics.
- Exporta resultados a CSV.
- Arquitectura modular separada en capas de configuracion, dominio y presentacion.

---

## Requisitos

- Python 3.11 o superior.
- Cuenta con acceso a Google Search Console.
- Credenciales OAuth Desktop de Google.

---

## Instalacion

```bash
git clone https://github.com/roderickzapata/gsc
cd gsc
python -m venv .venv
```

Activacion del entorno virtual:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Instalacion de dependencias**

```bash
pip install -r requirements.txt
```

---

## Configuracion

1. Copiar `config.example.json` a `config.json`:

```bash
cp config.example.json config.json
```

2. Descargar el archivo OAuth de Google desde [Google Cloud Console](https://console.cloud.google.com/apis/credentials) y guardarlo como `client_secret.json` en la raiz del proyecto.

3. Editar `config.json` y completar la propiedad `site_url` con la propiedad de Search Console:

```json
"site_url": "sc-domain:example.com"
```

Reemplazar `sc-domain:example.com` con la direccion de la propiedad configurada en Google Search Console.

**Filtros opcionales:** Para filtrar resultados de forma precisa, es posible usar uno o ambos filtros dentro de `query`:

```json
"query": {
  "dimensions": ["query", "page"],
  "type": "web",
  "row_limit": 1000,
  "page_filter": "https://www.example.com/pagina-especifica/",
  "query_filter": "mi producto"
}
```

- `page_filter`: filtra por URL exacta de la pagina.
- `query_filter`: filtra por texto exacto de la consulta de busqueda.

Cuando un filtro no esta configurado o es `null`, ese filtro no se aplica y la consulta devuelve todos los datos correspondientes.

### Variables de entorno

Las variables de entorno sobrescriben los valores correspondientes de `config.json`. Esto permite cambiar la configuracion sin modificar el archivo.

| Variable | Descripcion |
|----------|-------------|
| `GSC_SITE_URL` | URL de la propiedad de Search Console (formato: `sc-domain:example.com`). Si esta definida y no esta vacia, sobrescribe `gsc.site_url`. Si esta vacia, la validacion fallara. |
| `GSC_PAGE_FILTER` | URL exacta para filtrar resultados por pagina. Si esta definida y no esta vacia, sobrescribe `query.page_filter`. Si esta vacia (`""`), se interpreta como sin filtro (equivalente a `null`). Si no esta definida, se usa el valor de `config.json`. |
| `GSC_QUERY_FILTER` | Texto exacto para filtrar resultados por consulta de busqueda. Si esta definida y no esta vacia, sobrescribe `query.query_filter`. Si esta vacia (`""`), se interpreta como sin filtro (equivalente a `null`). Si no esta definida, se usa el valor de `config.json`. |

**Ejemplo:**

```bash
export GSC_SITE_URL="sc-domain:example.com"
export GSC_PAGE_FILTER="https://www.example.com/pagina-especifica/"
export GSC_QUERY_FILTER="mi producto"
python download.py --last 7
```

**Nota:** Si una variable de entorno se define pero se deja vacia (`""`), el filtro correspondiente no se aplica. Si no esta definida, se utiliza el valor de `config.json`.

---

## Primera ejecucion

La primera ejecucion abrira el navegador para autorizar el acceso a Google Search Console.

Una vez autorizado, se generara automaticamente el archivo `.token_cache.json` que almacenara las credenciales en cache para evitar repetir la autorizacion en ejecuciones posteriores.

---

## Uso

```bash
python download.py --last N
```

Descarga exactamente los ultimos N dias incluyendo hoy.

**Ejemplo:** Descargar los ultimos 7 dias:

```bash
python download.py --last 7
```

---

## Salida

El script genera un archivo CSV cuyo nombre se determina a partir de `gsc.site_url`. El directorio de salida se toma de `output.csv_path`, pero el nombre del archivo se genera automáticamente con el dominio extraído de `site_url`.

Por defecto, `output.csv_path` es `csv/export.csv`, lo que produce los archivos en el directorio `csv/` centralizado del proyecto. Por ejemplo, si `site_url` es `sc-domain:example.com`, el archivo resultante será `csv/example.com.csv`. Si se quiere otro destino, se puede cambiar `output.csv_path` en `config.json` (por ejemplo `data/export.csv` produciria `data/example.com.csv`). El directorio de salida se crea automaticamente si no existe.

**Columnas del CSV:**

- `query` — consulta de busqueda
- `page` — URL de la pagina
- `clicks` — numero de clics
- `impressions` — numero de impresiones
- `ctr` — ratio de clics (click-through rate)
- `position` — posicion promedio en resultados de busqueda

**Migracion desde una version anterior:** si se tienen CSVs de proyectos anteriores en la raiz (`dominio-a.com.csv`, `export.csv`, etc.), no se mueven automaticamente. Para reubicarlos dentro del directorio centralizado, copialos manualmente con un comando seguro, por ejemplo `mv *.com.csv csv/` (revisa antes que `*.com.csv` solo captura los CSVs deseados). Tras moverlos, ajusta `config.json` para que `output.csv_path` sea `csv/export.csv` o elimina ese campo del config para que tome el valor por defecto.

---

## Comparar dos sitios

`compare.py` toma dos CSVs ya exportados por `download.py` y produce un unico CSV agregado por consulta con la clasificacion de cada termino. **No** consulta la API, **no** accede a credenciales y **no** modifica los archivos de entrada.

La API de Search Analytics es por propiedad, por lo que primero se generan los CSV de cada sitio en ejecuciones independientes usando la variable de entorno `GSC_SITE_URL`. Los archivos se guardan en `csv/` (ver seccion anterior):

```bash
# Sitio A (los ultimos 30 dias incluyendo hoy)
GSC_SITE_URL="sc-domain:dominio-a.com" python download.py --last 30

# Sitio B (misma ventana temporal)
GSC_SITE_URL="sc-domain:dominio-b.com" python download.py --last 30
```

Esto produce `csv/dominio-a.com.csv` y `csv/dominio-b.com.csv` (el nombre del archivo se deriva del dominio de `site_url`).

A continuacion se ejecuta la comparacion, pasando los CSVs del directorio `csv/`:

```bash
python compare.py --site-a csv/dominio-a.com.csv --site-b csv/dominio-b.com.csv
```

Por defecto se genera `csv/comparison.csv` (crea el directorio si no existe). Se puede redirigir la salida con `--output`:

```bash
python compare.py --site-a csv/dominio-a.com.csv --site-b csv/dominio-b.com.csv --output reports/comparativa-30d.csv
```

Si el archivo ya existe, se sobrescribe.

**Argumentos del CLI:**

| Argumento | Obligatorio | Default | Descripcion |
|-----------|-------------|---------|-------------|
| `--site-a` | Si | — | Ruta del CSV del sitio A (exportado por `download.py`). Por convencion, dentro de `csv/`. |
| `--site-b` | Si | — | Ruta del CSV del sitio B. Por convencion, dentro de `csv/`. |
| `--output` | No | `csv/comparison.csv` | Ruta del CSV de salida. |

**Etiquetas y columnas del CSV de salida:**

El modulo acepta etiquetas configurables para que el nombre de las columnas refleje cada sitio. Los valores por defecto son `nica` y `lpc`:

| Columna | Descripcion |
|---------|-------------|
| `query` | Consulta de busqueda (union externa entre ambos CSVs, orden alfabetico). |
| `nica_clicks`, `nica_impressions`, `nica_ctr`, `nica_position` | Totales del sitio A para la consulta. `ctr` se recalcula como `clicks_total / impressions_total`; `position` se pondera por impresiones. |
| `lpc_clicks`, `lpc_impressions`, `lpc_ctr`, `lpc_position` | Totales del sitio B. |
| `status` | `shared` si la consulta aparece en ambos sitios; `only_nica` si solo aparece en A; `only_lpc` si solo aparece en B. |

Para una consulta que solo existe en uno de los dos sitios, las columnas del sitio ausente se emiten vacias.

**Validaciones de entrada:**

- Ambos CSVs deben existir y contener las columnas `query`, `page`, `clicks`, `impressions`, `ctr`, `position`.
- `--output` no puede coincidir con ninguno de los CSV de entrada (la comparacion se hace sobre rutas normalizadas con `Path.resolve()`, por lo que dos formas de escribir el mismo archivo, segmentos `..` o symlinks se detectan correctamente).
- `clicks`, `impressions` y `position` deben ser valores numericos finitos; `nan`, `inf` y `-inf` se rechazan con un mensaje que identifica archivo, fila, consulta y campo.
- Si se produce un error de validacion, no se genera el CSV de salida.

---

## Estructura del proyecto

```
gsc/
├── download.py          # Punto de entrada, orquesta el flujo completo
├── compare.py            # Compara dos CSVs exportados (post-procesamiento)
├── config.py            # Carga y validacion de configuracion
├── auth.py              # Autenticacion OAuth2
├── search_console.py    # Cliente de Google Search Console API
├── exporter.py          # Exportacion a CSV
├── models.py            # Modelos de datos: Config, ExecutionRequest, SearchResult
├── test_auth.py         # Script de prueba de autenticacion
├── test_compare.py      # Tests de compare.py
├── config.example.json  # Plantilla de configuracion
├── config.json          # Configuracion local (no versionar)
├── csv/                 # Directorio centralizado de CSVs (no versionado, ignorado por .gitignore)
│   └── example.com.csv  # CSV generado (nombre segun dominio)
```

**Responsabilidades:**

- `download.py` — Parsea argumentos, calcula el rango de fechas, orquesta la descarga y exportacion.
- `config.py` — Lee `config.json`, valida campos requeridos y construye el modelo `Config`.
- `auth.py` — Implementa el flujo OAuth2, gestiona la cache de tokens en `.token_cache.json`.
- `search_console.py` — Transforma la respuesta de Google Search Console en modelos `SearchResult`.
- `exporter.py` — Escribe los datos en formato CSV y determina el nombre del archivo a partir del dominio de `site_url`.
- `models.py` — Define los dataclasses `Config`, `ExecutionRequest` y `SearchResult`.
- `compare.py` — Modulo independiente de post-procesamiento. Lee dos CSVs, agrega por consulta (clics, impresiones, CTR recalculada, posicion ponderada) y emite un CSV clasificado por estado (`shared`, `only_nica`, `only_lpc`). No importa ningun otro modulo del proyecto.

---

## Arquitectura

- **Config** — Contiene la configuracion cargada desde `config.json`.
- **ExecutionRequest** — Representa la peticion de consulta con fechas, dimensiones, tipo y limite de filas.
- **SearchResult** — Representa una fila de datos de busqueda en el dominio de la aplicacion.
- `search_console.py` transforma la respuesta cruda de la API de Google en objetos `SearchResult`.

---

## Desarrollo

Los siguientes archivos contienen informacion local y no deben versionarse:

- `config.json`
- `client_secret*.json`
- `.token_cache.json`

Existe `config.example.json` como plantilla para nuevos desarrolladores.

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

Puedes utilizar, copiar, modificar y redistribuir este software de acuerdo con los terminos de dicha licencia.

La redistribucion del codigo fuente o de trabajos derivados debe conservar el siguiente aviso de copyright:

Copyright (c) 2026 Roderick Zapata | RYLCO

Consulta el archivo `LICENSE` para conocer los terminos completos de la licencia.
