# Changelog

El proyecto sigue [Versionado Semántico (Semantic Versioning)](https://semver.org/lang/es/).

---

## [Unreleased]

### Added

- Modulo `compare.py` para comparar dos CSV exportados por `download.py`, agregando clics, impresiones, CTR y posicion ponderada por consulta. Salida agregada por `query` con clasificacion `shared` / `only_nica` / `only_lpc` y union externa entre ambos sitios.
- CLI: `python compare.py --site-a A.csv --site-b B.csv [--output csv/comparison.csv]`.
- Funcion publica `compare_csvs(site_a_path, site_b_path, output_path, label_a="nica", label_b="lpc") -> Path` con validacion de rutas normalizadas (`Path.resolve()`), etiquetas no vacias ni iguales, y rechazo de valores no finitos (`nan`/`inf`/`-inf`) en `clicks`, `impressions` y `position`.

### Changed

- Centralizacion de los CSV de datos y resultados en el directorio `csv/` del proyecto. Por defecto, `download.py` guarda `csv/<domain>.csv` y `compare.py` guarda `csv/comparison.csv`. El directorio se crea automaticamente si no existe.
- `output.csv_path` en `config.json` ahora es opcional: su valor por defecto es `csv/export.csv`. La clave `output.csv_path` deja de ser un campo obligatorio (ADR-12).
- `.gitignore` añade `csv/` ademas del patron `*.csv` ya existente, para reflejar explicitamente el directorio centralizado.

## [1.0.0] - 2026-07-28

### Added

- Arquitectura modular separada en capas de configuración, dominio y presentación.
- Configuración mediante `config.json` con validación de campos requeridos.
- Plantilla `config.example.json` para nuevos desarrolladores.
- Autenticación OAuth2 con Google mediante `google-auth-oauthlib`.
- Descarga de Search Analytics desde Google Search Console API (`searchconsole` v1).
- Exportación de resultados a CSV con columnas: query, page, clicks, impressions, ctr, position.
- CLI con interfaz: `python download.py --last N`
- Punto de entrada instalable: `gsc-export`
- README completo con instrucciones de instalación, configuración y uso.
- Licencia MIT.
- Empaquetado mediante `pyproject.toml` con setuptools como backend.
- Auditoría arquitectónica completada que valida la separación de responsabilidades.
- Validación mediante prueba de integración real con Google Search Console.
