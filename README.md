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
git clone <repository-url>
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

El script genera un archivo CSV en la ruta especificada en `config.json`.

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
└── export.csv           # Archivo CSV generado
```

**Responsabilidades:**

- `download.py` — Parsea argumentos, calcula el rango de fechas, orquesta la descarga y exportacion.
- `config.py` — Lee `config.json`, valida campos requeridos y construye el modelo `Config`.
- `auth.py` — Implementa el flujo OAuth2, gestiona la cache de tokens en `.token_cache.json`.
- `search_console.py` — Transforma la respuesta de Google Search Console en modelos `SearchResult`.
- `exporter.py` — Escribe los datos en formato CSV con las columnas especificadas.
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
