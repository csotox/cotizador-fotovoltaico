# ADR-002: Gestión de compañias

## Contexto

Dentro del modelo SAAS las compañias son las empresas asociadas al usuario y que son las encargadas de generar las cotizaciones.

El sistema debe permitir que un usuario registrado pueda crear la empresa que emitira las cotizaciones.

La empresa debe quedar asociada al usuario que la ha creado.

## Decisión

- Debe ser una App de Django.
- Un usuario que es Staff no puede crear una empresa.
- Los nombres de las columnas se definen en inglés para mantener consistencia.
- Las empresas se eliminan de forma lógica (soft delete): la columna `deleted_at` marca el registro como eliminado sin borrarlo físicamente.

## Consecuencias

- La columna `id` del modelo conceptual corresponde al identificador público, implementado como `uuid` v4 según la convención de `AGENTS.md`.
- Además del `uuid`, el modelo mantiene un `id` autoincremental interno (convención de `AGENTS.md`) que no se expone en URLs, formularios ni interfaces.
- El borrado lógico permite la consulta de registros eliminados (`deleted_at` no nulo) y la recuperación futura.
- Los nombres de las columnas están en inglés: `address` (antes `direccion`).

## Modelo conceptual

### Compañias

Modelo de Compañias. Representa la empresa que genera la cotización.

```text
companies
- uuid
- name
- alias
- address
- rut
- email
- created_by
- created_at
- updated_at
- deleted_at
```

### Notas de implementación

- `uuid`: identificador público expuesto en URLs (v4, único, no editable).
- `id`: clave primaria autoincremental interna; no se expone (convención `AGENTS.md`).
- `rut` y `email` son obligatorios y únicos.
- `created_by`: usuario que creó la empresa (FK al usuario autenticado).
- `deleted_at`: soft delete. El queryset por defecto excluye los registros eliminados.