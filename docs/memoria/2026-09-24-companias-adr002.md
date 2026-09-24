# Memoria: Gestión de compañías (companies, ADR-002)

Fecha: 2026-09-24

## Modelo LLM utilizado

- opencode / big-pickle

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos" (Django 6.1, PostgreSQL, Bootstrap 5).
- Objetivo: implementar ADR-002 "Gestión de compañías" según AGENTS.md y habilidades `django-auth` y `system-ui`.

## Objetivo

- Permitir que un usuario registrado (no Staff) cree una empresa que emitirá cotizaciones.
- La empresa queda asociada al usuario creador.
- Implementar soft delete, usar `uuid` como identificador público y nombres de columnas en inglés.

## Decisiones tomadas (confirmadas con el usuario)

- Asociación usuario-empresa mediante FK `created_by` (sin modelo de membresía en este alcance).
- La columna `idx` del ADR se implementa como `uuid` v4 (convención AGENTS.md).
- `rut` y `email` obligatorios y únicos; `alias` y `address` opcionales.
- Implementar soft delete mediante `deleted_at` + manager que excluye registros eliminados.
- Nombres de columnas en inglés (`address` en lugar de `direccion`).
- ADR-002 actualizado: soft delete, inglés, `id` conceptual → `uuid`.

## Cambios realizados

### Archivos creados

- `cotizacion/companies/` (aplicación Django nueva)
  - `models.py`: `Company` con `id` (BigAutoField interno), `uuid` (v4 único no editable), `name`, `alias`, `address`, `rut` (único), `email` (único), `created_by` (FK PROTECT), `created_at`, `updated_at`, `deleted_at`. Manager/queryset con soft delete (`alive`, `dead`, `all_with_deleted`, `delete(hard=...)`, `hard_delete`).
  - `validators.py`: `validate_rut` (normalización, dígito verificador, formato `X.XXX.XXX-X`), `format_rut`, `normalize_rut`.
  - `forms.py`: `CompanyForm` (ModelForm) con clases `form-control`, validación de RUT, unicidad de `rut`/`email`, email normalizado a minúsculas.
  - `views.py`: `CompanyListView`, `CompanyCreateView`, `CompanyDetailView`. Login requerido, Staff → 403 (no crea empresas), lista/detalle aislados por `created_by`, detalle por `uuid`, URL de éxito al detalle, mensaje de éxito.
  - `urls.py`: namespace `companies` (`""`, `nueva/`, `<uuid:uuid>/`).
  - `admin.py`: `CompanyAdmin` con `uuid` read-only.
  - `tests.py`: 28 tests (modelo, soft delete, validaciones, vistas).
  - `migrations/0001_initial.py`.
  - `templates/companies/`: `list.html`, `form.html`, `detail.html`.
- `cotizacion/templates/partials/_form_fields.html`: partial compartido de campos de formulario.

### Archivos modificados

- `cotizacion/app_config/settings.py`: `companies` en `INSTALLED_APPS`.
- `cotizacion/app_config/urls.py`: `path('companies/', include('companies.urls'))`.
- `cotizacion/templates/base.html`: enlace "Empresas" en navbar (oculto para Staff); ajuste de `gap`/clases.
- `cotizacion/accounts/templates/accounts/home.html`: botones "Crear empresa"/"Mis empresas" (ocultos para Staff).
- `cotizacion/accounts/templates/accounts/login.html` y `signup.html`: apuntan al partial compartido `partials/_form_fields.html`.
- `docs/ADR/adr002-company.md`: soft delete documentado, columnas en inglés (`address`) y columna conceptual `id` → `uuid`.

### Archivos eliminados

- `cotizacion/accounts/templates/accounts/partials/_form_fields.html` (reemplazado por partial compartido).

## Problemas encontrados

- `format_rut` agrupaba los miles desde la izquierda: RUT `12.345.678-5` se guardaba como `12345.678-5`. Esto rompía la unicidad (duplicados no detectados) y la normalización. Corregido agrupando desde la derecha.
- `test_detail_uses_uuid_url`: `assertNotIn(str(pk), url)` era inválido porque el pk puede aparecer dentro del uuid (dígitos hexadecimales); se reemplazó por comparación directa de la URL.
- Al instrumentar un test fallido se verificó que la causa raíz era el bug de `format_rut` (respuesta 302 en vez de formulario con error); tras la corrección, el flujo pasó.

## Dificultades

- Ninguna relevante fuera de lo indicado.

## Pendientes

- Unicidad de `rut`/`email` incluye registros soft-deleted: un RUT/correo eliminado bloquea su reutilización hasta `hard_delete`.
- Modelo de membresía multi-usuario (`CompanyMember`) fuera de alcance (posible ADR futuro).
- Flujo de eliminación (interfaz) no implementado; solo existe el mecanismo soft delete en el modelo.
- Verificación visual con Playwright pendiente (flujo `companies`).

## Comandos ejecutados

- `python ./cotizacion/manage.py startapp companies cotizacion/companies`
- `python ./cotizacion/manage.py makemigrations companies`
- `python ./cotizacion/manage.py check` (sin issues)
- `python ./cotizacion/manage.py test companies accounts` (43/43 OK)
- `python ./cotizacion/manage.py migrate`
- Smoke test con `django.test.Client`: GET `nueva/` 200, GET list 200, POST `nueva/` 302 → `/companies/<uuid>/`, GET detail 200. RUT normalizado `12.345.678-5`, email en minúsculas, `created_by` asignado.

## Resultado final

- App `companies` implementada y validada (43 tests OK, `manage.py check` OK).
- Flujo: login → `/companies/nueva/` → POST → redirect `/companies/<uuid>/`.
- Staff no puede crear empresas (403). Lista y detalle aislados por usuario creador.
