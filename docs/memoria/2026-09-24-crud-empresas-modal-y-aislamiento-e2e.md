# Memoria: CRUD de empresas (acciones, edición, modal) y aislamiento de tests E2E

Fecha: 2026-09-24

## Modelo LLM utilizado

- opencode / big-pickle

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos" (Django 6.1, PostgreSQL, Bootstrap 5, jQuery 4).
- Continuación de las memorias `2026-09-24-companias-adr002.md` (app `companies`) y `2026-09-24-aislamiento-bd-tests.md` (pytest-django sobre `test_cotizador`).
- En `accounts/home.html` existía la tabla de empresas del usuario sin columna de acciones.

## Objetivo

- Agregar columna de acciones (Eliminar y luego Editar) a la tabla de empresas.
- Verificar que la eliminación usa soft delete.
- Cambiar el flujo: después de guardar, "Volver" apunta a `/` (home); eliminar la vista/pantalla `list`.
- Crear un componente modal base para crear/editar distintos dominios, migrando primero el form de empresas.
- Garantizar que los tests (unitarios y Playwright E2E) corran sobre la BD de test y no sobre la BD de desarrollo (`cotizador`).

## Cambios realizados

### CRUD y flujo (soft delete + edición)

- `companies/views.py`
  - Agregado `CompanyDeleteView` (solo POST vía `http_method_names=["post"]`): soft delete (`Company.delete()`), queryset restringido a `created_by`, Staff → 403, ajeno/eliminada → 404, redirect a `home`. Validado que el delete usa el soft delete del modelo (`deleted_at`).
  - Agregado `CompanyUpdateView`: reutiliza `CompanyForm`, template parcial, restricciones iguales, redirect al detalle.
  - Eliminado `CompanyListView` y el import de `ListView`.
- `companies/urls.py`
  - Agregadas rutas `editar/` y `eliminar/` (namespace `companies:update`, `companies:delete`).
  - Eliminada la ruta raíz (`companies:list`).
- `companies/forms.py`
  - Fix: la validación de unicidad de `rut`/`email` no excluía la instancia actual, rompiendo la edición. Ahora `exclude(pk=self.instance.pk)` cuando existe.
- `companies/templates/companies/`
  - Eliminados: `list.html` y `form.html`.
  - Creado: `_form.html` (parcial, con `action` dinámica crear/editar según `form.instance.pk`).
- `accounts/templates/accounts/home.html`
  - Columna "Acciones" con botones Editar y Eliminar (POST con confirm nativo).
  - Botón "Crear empresa" y "Editar" pasan a abrir la modal.
- Otros apuntan a `home`: `templates/base.html` (navbar), `detail.html` (Volver).
- `companies/tests.py`
  - Agregados `CompanyDeleteViewTests`, `CompanyUpdateViewTests` y `CompanyModalFormTests`.
  - Eliminado `CompanyListViewTests`.

### Servidor de desarrollo

- El proceso `runserver 0.0.0.0:8000` quedó colgado (no respondía, HTTP 000) con módulos viejos en memoria (`module 'companies.views' has no attribute 'CompanyListView'`). Se mató (SIGKILL) y se reinició; el código ya era correcto.

### Componente modal base (AJAX)

- `app_config/settings.py`
  - Agregado `STATICFILES_DIRS = [BASE_DIR / 'static']`.
- `templates/base.html`
  - CDN de jQuery 4 antes del bundle de Bootstrap.
  - Slot de modal genérico `#appModal` (header `#appModalLabel`, body `#appModalBody`).
  - `<script src="{% static 'js/modal.js' %}">`.
- `cotizacion/static/js/modal.js` (nuevo)
  - Abre la modal con `bootstrap.Modal` y carga el contenido por `$.get`.
  - Submit AJAX: `data: serialize() + "&form=modal"`, `dataType: "text"`. En éxito cierra y recarga; en error reinyecta el form con errores.
- `companies/mixins.py` (nuevo)
  - `ModalFormMixin`: detecta `form=modal`, éxito devuelve `JsonResponse({"success": True})`, inválido renderiza el parcial con errores. Reutilizable por otros dominios.
- `companies/views.py`
  - `CompanyCreateView` y `CompanyUpdateView` usan `ModalFormMixin` y `template_name = "companies/_form.html"`.

### Tests E2E sobre base de datos de test

- `conftest.py` (raíz, nuevo)
  - Guardia autouse que falla si `DATABASES.default.NAME` no empieza con `test_` (unitarios y E2E).
- `cotizacion/test/e2e/test_company_modal.py` (nuevo)
  - Usa `live_server` de pytest-django (sobre `test_cotizador`) y `sync_playwright` manual.
  - Sembrado con ORM; casos: crear y editar vía modal.
- `cotizacion/test/e2e/test_home.py`
  - Eliminado (stub roto, usaba `localhost:8000`).
- `pytest.ini`
  - Marker actualizado: `e2e usa live_server sobre la base de datos de test (test_cotizador)`.
- `Makefile`
  - Comentarios: `run-server` marcado como servidor de desarrollo (BD dev, no usar en tests); `test-e2e` documentado sin servidor externo.
- `AGENTS.md`
  - Nueva sección `## Testing` con restricciones obligatorias (BD de test, `live_server`, comandos `pytest`/`pytest -m e2e`, verificación de que `cotizador` no recibe escrituras).

## Problemas encontrados

- `GET` del `DeleteView` renderizaba un template de confirmación inexistente → restringido a `POST` (405 en GET).
- La unicidad de `rut`/`email` en edición: al no excluir la instancia, el guardado devolvía el formulario (200) en vez de guardar.
- `modal.js`: `$.parseJSON` no existe en jQuery 3/4 → reemplazado por `JSON.parse`.
- `modal.js`: `$.ajax` auto-detectaba el `application/json` y pasaba un objeto a los handlers → se forzó `dataType: "text"`.
- pytest-playwright levantaba un event loop incompatible con el acceso síncrono a la BD de Django (`SynchronousOnlyOperation` en la creación de la BD de test). Se resolvió no usando las fixtures `page`/`browser` y lanzando `sync_playwright()` dentro del test.
- El seed E2E inicial usaba subprocess con `manage.py shell` sobre la BD dev y el servidor humano `:8000`; corregido con `live_server` + ORM.

## Decisiones tomadas (confirmadas con el usuario)

- Eliminar por completo la pantalla `list` (duplicaba `home`); "Volver"/"Cancelar"/navbar → `home`.
- Enfoque AJAX con modal genérica (no include estático) como componente base para futuros dominios.
- Eliminar las páginas standalone de crear/editar (acceso solo vía modal), manteniendo las URLs como fallback defensivo.
- Agregar jQuery 4 (CDN) y directorio `static/` (autorizado; jQuery ya estaba en el stack).
- Tests E2E con `live_server` compartido sobre `test_cotizador` (no BD E2E dedicada).
- Eliminar el stub `test/e2e/test_home.py`.

## Dificultades

- Diagnóstico de la interacción entre pytest-playwright (asyncio) y Django (BD síncrona) en el mismo hilo.
- La modal en home carga un form cuyo `action` explícito debe ser la URL crear/editar (no se puede publicar a la URL de la página `/`).

## Pendientes

- La unicidad de `rut`/`email` incluye soft-deleted (heredado; citado en `2026-09-24-companias-adr002.md`).
- Documentar el componente modal base como ADR si requiere justificación permanente (sugerido, no creado en esta sesión).

## Comandos ejecutados

- `python manage.py check` (OK)
- `python manage.py test companies accounts` (58 passed)
- `pytest` (58 passed, 2 deselected)
- `pytest -m e2e` (2 passed)
- Reinicio del servidor dev: kill del proceso `runserver` + `nohup python ./cotizacion/manage.py runserver 0.0.0.0:8000`
- Verificación post-tests sobre `cotizador`: `E2E companies = 0`, `e2e users = 0` (BD dev intacta).
- Screenshots Playwright regenerados en `.pytest_cache/capturas/` (`modal_formulario.png`, `modal_creada.png`, `modal_editar.png`, `modal_editada.png`).

## Resultado final

- CRUD de empresas operativo: Editar (modal) y Eliminar (soft delete) en `home`, flujo único con feedback a `home`.
- Componente modal base AJAX funcional y validado (crear y editar empresa); listo para reutilizar en otros dominios.
- Tests aislados: unitarios (`pytest`) y E2E (`pytest -m e2e` con `live_server`) corren sobre `test_cotizador`; `conftest.py` impide usar la BD de desarrollo; AGENTS.md documenta las restricciones.
