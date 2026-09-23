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

## Validación

Después de modificar templates:
- Verificar renderizado.
- Revisar formularios.
- Revisar mensajes de error.
- Revisar navegación.
- Verificar que no se rompa comportamiento existente.
