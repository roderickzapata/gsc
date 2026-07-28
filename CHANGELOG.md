# Changelog

El proyecto sigue [Versionado Semántico (Semantic Versioning)](https://semver.org/lang/es/).

---

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
