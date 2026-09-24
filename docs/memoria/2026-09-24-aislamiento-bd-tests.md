# Memoria: Aislamiento de tests con base de datos temporal

Fecha: 2026-09-24

## Modelo LLM utilizado

- opencode / big-pickle

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos" (Django 6.1, PostgreSQL, Bootstrap 5).
- `DATABASES.default` apuntaba a `POSTGRES_DB=cotizador` sin clave `TEST`.
- Se detectó que los tests podían ejecutarse contra la base de datos real `cotizador`.

## Objetivo

- Garantizar que los tests corran sobre su propia base de datos temporal (`test_cotizador`) y nunca sobre `cotizador`.

## Cambios realizados

### Archivos modificados

- `cotizacion/app_config/settings.py`
  - Eliminado el alias `sqlite` huérfano de `DATABASES` (dejando solo `default`).
  - Agregada clave `TEST` con `NAME: "test_cotizador"` al `default`.
- `.devcontainer/requirements.txt`
  - Agregado `pytest-django`.
- `cotizacion/test/e2e/test_home.py`
  - Marcado `test_home` con `@pytest.mark.e2e`.
- `Makefile`
  - Agregados targets `test` (`pytest`) y `test-e2e` (`pytest -m e2e`).

### Archivos creados

- `pytest.ini` (raíz)
  - `DJANGO_SETTINGS_MODULE = app_config.settings`
  - `pythonpath = cotizacion`
  - `python_files = test_*.py *_test.py tests.py` (incluye los `tests.py` de las apps)
  - `addopts = -m "not e2e" -ra`
  - Marker `e2e` documentado.

## Problemas encontrados

- `pytest-django` no encontraba el proyecto Django (`No module named 'app_config'`) porque el proyecto vive en `cotizacion/`. Resuelto agregando `pythonpath = cotizacion` al `pytest.ini`.
- El Dockerfile `pytest-django` no se instaló en la imagen; por instrucción del usuario se instaló directamente con `pip install pytest-django` sin reiniciar el contenedor.

## Decisiones tomadas (confirmadas con el usuario)

- `pytest` + `pytest-django` como runner oficial de tests.
- Eliminar el alias `sqlite` huérfano de `settings.py`.
- Los tests E2E (Playwright) usan el servidor en vivo (base real) y quedan excluidos del run por defecto; se ejecutan con `pytest -m e2e`.

## Pendientes

- Ninguno aplicable a esta tarea.

## Comandos ejecutados

- `python -m pip install pytest-django`
- `python ./cotizacion/manage.py check` (sin issues)
- `pytest --collect-only -q` (43/44 recolectados, 1 deseleccionado: e2e)
- `pytest -q` (43 passed, 1 deselected)
- `psql ... -c "\l"` (verificación: `test_cotizador` creado y eliminado al finalizar; solo queda `cotizador`)
- `psql ... cotizador -c "SELECT ... test_users"` (`test_users = 0`: sin datos de prueba en `cotizador`)

## Resultado final

- Tests aislados: `pytest` ejecuta 43 tests sobre `test_cotizador` (temporal, creada y destruida por run) y `cotizador` queda intacta.
- Runner oficial: `make test` (`pytest`) y `make test-e2e` (`pytest -m e2e`).