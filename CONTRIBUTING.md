# Contributing

Gracias por tu interés en contribuir a este proyecto.

---

## Filosofía del proyecto

La arquitectura se diseña antes de implementarse. Toda implementación debe respetar los contratos aprobados y las decisiones arquitectónicas tomadas.

Cada módulo tiene responsabilidades claramente definidas y no debe introducir dependencias innecesarias.

---

## Flujo de contribución

Los cambios deben:

- Mantener la arquitectura existente.
- Respetar las interfaces públicas de cada módulo.
- Mantener la separación de responsabilidades entre capas.
- Aplicar la política Fail Fast cuando corresponda (validación anticipada con errores claros).

---

## Cambios arquitectónicos

Cualquier modificación que afecte alguna de las siguientes áreas debe documentarse antes de implementarse:

- Interfaces públicas de los módulos.
- Modelos de dominio (`Config`, `ExecutionRequest`, `SearchResult`).
- Flujo de ejecución entre módulos.
- Contratos de datos entre capas.

---

## Calidad

Antes de enviar una contribución, verifica que:

- El proyecto funciona correctamente con `python download.py --last N`.
- No se rompen contratos existentes entre módulos.
- La documentación permanece sincronizada con el código.
- El README refleja el comportamiento real del programa.
- La licencia MIT permanece intacta.

---

## Estilo

- Código claro y legible.
- Funciones pequeñas con una única responsabilidad.
- Nombres descriptivos para funciones, variables y módulos.
- Comentarios únicamente cuando aporten valor real al lector.

---

## Versionado

El proyecto utiliza [Semantic Versioning](https://semver.org/lang/es/).

Las nuevas funcionalidades deben registrarse en `CHANGELOG.md` bajo la sección `[Unreleased]` hasta la siguiente versión publicada.
