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

**Filtro opcional por pagina:** Para filtrar resultados por una URL exacta, agregar `page_filter` dentro de `query`:

```json
"query": {
  "dimensions": ["query", "page"],
  "type": "web",
  "row_limit": 1000,
  "page_filter": "https://www.example.com/pagina-especifica/"
}
```

Cuando `page_filter` no esta configurado o es `null`, la consulta devuelve todos los datos igual que antes.

### Variables de entorno

Las variables de entorno sobrescriben los valores correspondientes de `config.json`. Esto permite cambiar la configuracion sin modificar el archivo.

| Variable | Descripcion |
|----------|-------------|
| `GSC_SITE_URL` | URL de la propiedad de Search Console (formato: `sc-domain:example.com`). Si esta definida y no esta vacia, sobrescribe `gsc.site_url`. Si esta vacia, la validacion fallara. |
| `GSC_PAGE_FILTER` | URL exacta para filtrar resultados por pagina. Si esta definida y no esta vacia, sobrescribe `query.page_filter`. Si esta vacia (`""`), se interpreta como sin filtro (equivalente a `null`). Si no esta definida, se usa el valor de `config.json`. |

**Ejemplo:**

```bash
export GSC_SITE_URL="sc-domain:example.com"
export GSC_PAGE_FILTER="https://www.example.com/pagina-especifica/"
python download.py --last 7
```

**Nota:** Si `GSC_PAGE_FILTER` se define pero se deja vacia, la consulta devolvera todos los datos sin filtrar por pagina.

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

Por ejemplo, si `site_url` es `sc-domain:example.com`, el archivo resultante será `example.com.csv`. Si `csv_path` es `data/export.csv`, el resultado será `data/example.com.csv`.

**Columnas del CSV:**

- `query` — consulta de busqueda
- `page` — URL de la pagina
- `clicks` — numero de clics
- `impressions` — numero de impresiones
- `ctr` — ratio de clics (click-through rate)
- `position` — posicion promedio en resultados de busqueda

---

## Estructura del proyecto

```
gsc/
├── download.py          # Punto de entrada, orquesta el flujo completo
├── config.py            # Carga y validacion de configuracion
├── auth.py              # Autenticacion OAuth2
├── search_console.py    # Cliente de Google Search Console API
├── exporter.py          # Exportacion a CSV
├── models.py            # Modelos de datos: Config, ExecutionRequest, SearchResult
├── test_auth.py         # Script de prueba de autenticacion
├── config.example.json  # Plantilla de configuracion
├── config.json          # Configuracion local (no versionar)
└── example.com.csv # Archivo CSV generado (nombre segun dominio)
```

**Responsabilidades:**

- `download.py` — Parsea argumentos, calcula el rango de fechas, orquesta la descarga y exportacion.
- `config.py` — Lee `config.json`, valida campos requeridos y construye el modelo `Config`.
- `auth.py` — Implementa el flujo OAuth2, gestiona la cache de tokens en `.token_cache.json`.
- `search_console.py` — Transforma la respuesta de Google Search Console en modelos `SearchResult`.
- `exporter.py` — Escribe los datos en formato CSV y determina el nombre del archivo a partir del dominio de `site_url`.
- `models.py` — Define los dataclasses `Config`, `ExecutionRequest` y `SearchResult`.

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
