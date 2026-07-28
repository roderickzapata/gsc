# Contexto del Proyecto - Google Search Console API

## 1. Autenticación

### Flujo de Autenticación Recomendado

**OAuth 2.0 para Aplicaciones Instaladas (Installed App Flow)**

El flujo recomendado para scripts locales ejecutados manualmente es el OAuth 2.0 para Aplicaciones Instaladas:

1. Envía al usuario al navegador para autenticarse y dar consentimiento.
2. El servidor devuelve un código de autorización a la aplicación vía un servidor local.
3. La aplicación intercambia el código por un access token y refresh token.
4. Los tokens se almacenan para uso posterior y se auto-refrescan automáticamente.

**Nota:** La documentación oficial no recomienda el flujo de "Application Default Credentials" (`gcloud auth application-default login`) para este caso de uso, ya que está diseñado principalmente para aplicaciones que se ejecutan en infraestructura de Google Cloud (Compute Engine, Cloud Run, etc.).

### Bibliotecas Oficiales de Python Recomendadas

| Biblioteca | Propósito |
|------------|-----------|
| **google-api-python-client** | Cliente principal para acceder a las APIs de Google (incluyendo Search Console) |
| **google-auth-library-python** | Gestión de credenciales y autenticación |
| **google-auth-oauthlib** | Proporciona `InstalledAppFlow` para el flujo de aplicaciones instaladas |

La clase `InstalledAppFlow` de `google_auth_oauthlib.flow` es la implementación oficial para aplicaciones de escritorio y scripts locales.

### Scope Mínimo Requerido

| Scope | Acceso |
|-------|--------|
| `https://www.googleapis.com/auth/webmasters.readonly` | Solo lectura (mínimo para consultas de Search Analytics) |
| `https://www.googleapis.com/auth/webmasters` | Lectura y escritura |

### Configuración Previa en Google Cloud

1. **Crear un Proyecto en Google Cloud**
   - Ir a Google Cloud Console y crear un nuevo proyecto.

2. **Habilitar la API de Search Console**
   - Navegar a "APIs y Servicios" > "Biblioteca".
   - Buscar "Google Search Console API" y habilitarla.

3. **Crear Credenciales OAuth 2.0**
   - Ir a "APIs y Servicios" > "Credenciales".
   - Click en "Crear Credenciales" > "ID de cliente de OAuth".
   - Seleccionar tipo: **"Aplicación instalada"** (Installed application).
   - Descargar el archivo `client_secrets.json`.

4. **Configuración Adicional**
   - El usuario final debe tener una cuenta de Google con permisos en Search Console (sitio verificado).

### Enlaces a Documentación Oficial

- Google Search Console API - Autorización y Scopes:
  https://developers.google.com/webmaster-tools/v1/how-tos/authorizing

- Google Search Console API - Quickstart Python:
  https://developers.google.com/webmaster-tools/v1/quickstart/quickstart-python

- Google Search Console API - Prerrequisitos:
  https://developers.google.com/webmaster-tools/v1/prereqs

- Google API Python Client - OAuth para Aplicaciones Instaladas:
  https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth-installed.md

- Google Auth Library Python - Documentación:
  https://googleapis.dev/python/google-auth/latest/user-guide.html

- google-auth-oauthlib - InstalledAppFlow:
  https://googleapis.github.io/google-api-python-client/docs/oauth

---

## 2. Search Analytics API

### Endpoint

```
POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query
```

### Parámetros del Cuerpo de la Petición

#### Parámetros Obligatorios

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| **startDate** | string | Fecha de inicio del rango en formato `YYYY-MM-DD`. |
| **endDate** | string | Fecha de fin del rango en formato `YYYY-MM-DD`. |

#### Parámetros Opcionales

| Parámetro | Tipo | Descripción | Valores Permitidos |
|-----------|------|-------------|-------------------|
| **dimensions** | array[string] | Dimensiones para agrupar los resultados. | `"query"`, `"page"`, `"country"`, `"device"`, `"date"`, `"searchAppearance"` |
| **type** | string | Filtra resultados por tipo de búsqueda. | `"web"`, `"image"`, `"video"`, `"news"`, `"discover"`, `"googleNews"` |
| **aggregationType** | string | Cómo se agregan los datos. Por defecto es `"auto"`. | `"auto"`, `"byPage"`, `"byProperty"`, `"byNewsShowcasePanel"` |
| **rowLimit** | integer | Número máximo de filas a devolver. Por defecto es 1000. | Entero entre 1 y 25,000 |
| **startRow** | integer | Índice basado en cero de la primera fila a devolver (paginación). | Entero >= 0 (default: 0) |
| **dimensionFilterGroups** | array[object] | Grupos de filtros a aplicar. | Ver estructura abajo |

### Estructura de `dimensionFilterGroups`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **groupType** | string | Indica cómo se combinan los filtros dentro del grupo. |
| **filters** | array[object] | Lista de filtros. |

#### Estructura de cada filtro:

| Campo | Tipo | Descripción | Valores Permitidos |
|-------|------|-------------|-------------------|
| **dimension** | string | La dimensión a filtrar. | `"query"`, `"page"`, `"country"`, `"device"`, `"searchAppearance"` |
| **operator** | string | Operador de comparación. | `"equals"`, `"contains"`, `"notContains"`, expresión RE2 (regex) |
| **expression** | string | Valor o patrón de filtrado. | Depende del operador y dimensión |

### Valores de Dimensiones y Filtros

#### Dimensiones Disponibles para Agrupar (`dimensions`)
- `"query"` — Término de búsqueda
- `"page"` — URL de la página
- `"country"` — Código de país ISO 3166-1 alpha-3 (ej: `"IND"`, `"USA"`)
- `"device"` — Tipo de dispositivo
- `"date"` — Fecha en formato `YYYY-MM-DD`
- `"searchAppearance"` — Tipo de apariencia en search results

#### Valores de `device`
- `"MOBILE"`
- `"DESKTOP"`
- `"TABLET"`

#### Valores de `type` (tipo de búsqueda)
- `"web"` — Resultados web normales
- `"image"` — Búsqueda de imágenes
- `"video"` — Búsqueda de videos
- `"news"` — Búsqueda de noticias
- `"discover"` — Google Discover
- `"googleNews"` — Google News

#### Tipos de `aggregationType`

| Valor | Descripción |
|-------|-------------|
| `"auto"` | La API selecciona automáticamente el tipo de agregación. Valor por defecto. |
| `"byPage"` | Agrega datos por URI canónico. Necesario para conteos precisos cuando se agrupa por página. |
| `"byProperty"` | Agrega datos a nivel de propiedad. **No soportado** para tipos `discover` o `googleNews`. |
| `"byNewsShowcasePanel"` | Agrega datos por panel de escaparate de noticias. Requiere filtro específico de searchAppearance. |

#### Operadores de Filtro

- `"equals"` —Coincidencia exacta (no distingue mayúsculas para `country` y `device`).
- `"contains"` —Coincidencia por subcadena (no distingue mayúsculas para `country` y `device`).
- `"notContains"` — Exclusión por subcadena.
- Expresiones RE2 —Se soporta regex para patrones más complejos.

#### Ejemplos de expresiones de filtro:
```
country equals FRA
query contains mobile use
device notContains tablet
```

### Estructura de la Respuesta

#### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **rows** | list | Lista de filas agrupadas por las claves de dimensión. |
| **responseAggregationType** | string | Indica cómo se agregaron los resultados (`"auto"`, `"byPage"`, `"byProperty"`). |
| **metadata** | object | Metadata sobre el estado de los datos (opcional). |

#### Estructura de cada Row (`rows[]`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **keys** | list[string] | Valores de dimensión para esa fila, en el orden especificado en la query. |
| **clicks** | double | Número de clics para esa fila. |
| **impressions** | double | Número de impresiones para esa fila. |
| **ctr** | double | Click Through Rate (0 a 1.0). |
| **position** | double | Posición promedio en resultados de búsqueda. |

#### Estructura de `metadata` (cuando está presente)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **first_incomplete_date** | string | Primera fecha para la cual aún se están recopilando datos (`YYYY-MM-DD`). |
| **first_incomplete_hour** | string | Primera hora con datos incompletos (formato ISO-8601). |

### Limitaciones y Consideraciones Documentadas

#### Límites de Filas y Paginación

| Aspecto | Límite |
|---------|--------|
| **rowLimit** mínimo | 1 |
| **rowLimit** máximo | 25,000 |
| **rowLimit** por defecto | 1,000 |
| **startRow** | Basado en cero (0, 1, 2, ...) |

#### Límites de Datos

| Aspecto | Límite |
|---------|--------|
| **Filas por día por tipo de búsqueda** | Máximo 50,000 filas de datos por día para cada tipo (`web`, `image`, etc.), ordenadas por clics. |
| **Rango de fechas** | Debe ser de uno o más días. |
| **Retrieval de datos** | Si la query devuelve menos filas que el `rowLimit` solicitado, se han recuperado todos los datos. |

#### Comportamiento de los Resultados

- Los resultados se **ordenan por clics en orden descendente**.
- Para clics idénticos, el orden es arbitrario.
- **Las filas sin datos para un día específico se omiten** (especialmente relevante al usar dimensión `date`).
- **Los datos pueden no estar disponibles para todo el rango** especificado, especialmente los días más recientes (data freshness).

#### Restricciones de Agregación

- `aggregationType="byProperty"` **no es compatible** con tipos `discover` ni `googleNews`.
- Agrupar o filtrar por `page` **impide** la agregación por propiedad.
- Para conteos **exactos al agrupar por página**, se debe usar `aggregationType="byPage"` **sin** incluir las dimensiones `page` ni `query` en la petición.

#### Búsqueda por Search Appearance

- Para filtrar por `searchAppearance`, primero se debe hacer una query agrupando **solo** por esa dimensión para identificar los tipos disponibles.
- Luego se realiza una segunda query filtrando por el tipo específico.

### Enlaces a Documentación Oficial

- Referencia completa del método `searchanalytics/query`:
  https://developers.google.com/webmaster-tools/v1/searchanalytics/query

- Guía de Search Analytics - Conceptos y ejemplos:
  https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics

- Guía "All Your Data" - Detalles de agregación y limitaciones:
  https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data

- Índice de la API v1:
  https://developers.google.com/webmaster-tools/v1/api_reference_index

- Quickstart Python oficial:
  https://developers.google.com/webmaster-tools/v1/quickstart/quickstart-python
