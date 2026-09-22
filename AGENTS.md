# Project Instructions

## Project
Cotizador de sistemas fotovoltaicos.

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

