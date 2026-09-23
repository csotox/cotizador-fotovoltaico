---
name: system-ui
description: Implementa y revisa templates Django consistentes usando Bootstrap 5 y jQuery.
---

# System UI

## Objetivo

Mantener una interfaz consistente en todos los templates existentes y nuevos.

## Reglas

- Todos los templates deben extender una plantilla base común.
- Usar Bootstrap 5 para layout, formularios, tablas, alertas, navegación y botones.
- Usar jQuery únicamente para interacciones simples del frontend.
- Evitar estilos inline salvo casos justificados.
- Reutilizar componentes existentes antes de crear otros nuevos.
- Mantener consistencia en:
  - navbar
  - breadcrumbs
  - títulos
  - formularios
  - botones
  - tablas
  - mensajes de error y éxito

## Formularios

- Usar clases Bootstrap en inputs, selects y textareas.
- Mostrar errores de validación cerca del campo correspondiente.
- Mantener acciones principales y secundarias visualmente consistentes.

## Templates nuevos

Antes de crear un template nuevo:
- Revisar la plantilla base.
- Revisar templates similares existentes
- Reutilizar estructura y componentes.

## Templates existentes

Al modificar templates existentes:
- No cambiar lógica funcional.
- Mejorar únicamente estructura y presentación.
- Mantener URLs, nombres de campos y comportamiento existente.

## Validación con Playwright

Después de modificar templates:

- Si el frontend ya está levantado en `http://localhost:5173`, el agente no debe reutilizar ese servidor para Playwright.
- Ejecutar los tests E2E relacionados.
- Usar Playwright para verificar el flujo afectado.
- Revisar errores visibles en la interfaz.
- Toda corrección visual debe validarse en navegador real con Playwright cuando el proyecto lo tenga disponible.
- No reportar una corrección visual como terminada solo porque pasan `typecheck` y tests unitarios.
- Cuando valide con Playwright, debe reportar el flujo ejecutado y, si toma screenshots, la ruta de los archivos.
- Graba las screenshots en `workspace/.pytest_cache/capturas/`
