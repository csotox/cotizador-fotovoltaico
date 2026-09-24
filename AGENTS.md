# Project Instructions

## Project
Cotizador de sistemas fotovoltaicos.

## Documentación del projecto

Antes de realizar cambios, revisa la documentación del proyecto:

- `docs/product.md` Definición del proyecto, alcance, MVP.
- `docs/architecture.md` — Arquitectura, módulos y restricciones técnicas del proyecto.
- `docs/domain.md` — Conceptos del dominio, responsabilidades y relaciones entre entidades.

## Stack
- Python 3.13
- Django 6.1
- PostgreSQL 16
- Bootstrap 5
- jQuery 4
- Docker / Dev Container

## General rules
- No agregar nuevas tecnologías sin autorización.
- No cambiar la arquitectura del proyecto sin autorización.
- No instalar dependencias sin justificar su necesidad.
- Mantener el código simple y legible.
- Priorizar funcionalidades del MVP.
- No almacenar secretos en el repositorio.
- Al finalizar de leer este archivo deja un mensaje en el chat que indique: AGENTS leido

## Development workflow
Antes de modificar código:

1. Revisar los archivos relacionados.
2. Explicar brevemente qué se va a modificar.
3. Realizar cambios pequeños.
4. Ejecutar las validaciones correspondientes.
5. Informar qué archivos fueron modificados.

## Django
- Utilizar el ORM de Django.
- Utilizar migraciones para cambios de base de datos.
- Evitar SQL directo salvo que exista una razón técnica.
- Mantener separadas presentación, lógica y persistencia.
- Presentación utilizar los `templates` de Django

## Validation
Después de realizar cambios:

- Ejecutar `python manage.py check`.
- Ejecutar tests relacionados si existen.
- Verificar que no existan errores evidentes.

## Testing
Reglas obligatorias al ejecutar tests:

- Todos los tests, unitarios y E2E/Playwright, se ejecutan contra la base de datos de test `test_cotizador`.
- Prohibido ejecutar tests contra la base de datos de desarrollo (`cotizador`).
- Prohibido sembrar o inspeccionar datos con `manage.py shell`, `manage.py dbshell` o scripts dentro de los tests.
  - Tests unitarios: usar el ORM con las fixtures `django_db` (o el test runner de Django).
  - Tests E2E: usar la fixture `live_server` de pytest-django y sembrar con el ORM dentro del test.
- Prohibido ejecutar tests E2E contra `http://localhost:8000` (servidor de desarrollo humano). Usar `live_server`.
- Prohibido apuntar `POSTGRES_DB` ni settings a la base de datos de desarrollo en contexto de test.
- Comandos canónicos:
  - Tests unitarios: `pytest`.
  - Tests E2E: `pytest -m e2e` (no requiere servidor externo; `live_server` levanta uno sobre la BD de test).
- Después de ejecutar tests, verificar que la BD de desarrollo no recibió escrituras.

## Convenciones de modelos Django

- Todos los modelos de negocio deben utilizar un `id` autoincremental como clave primaria interna.
- El campo `id` es de uso interno y no debe exponerse en URLs, formularios ni interfaces públicas.
- Todos los modelos de negocio deben incluir un campo `uuid` versión 4.
- El `uuid` debe ser único y no editable.
- El `uuid` será el identificador utilizado en URLs y referencias expuestas al frontend.

Código esperado en un modelo de Django:
~~~ Python
id = models.BigAutoField(primary_key=True)

uuid = models.UUIDField(
    default=uuid.uuid4,
    unique=True,
    editable=False
)
~~~
