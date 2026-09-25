# Memoria: Gestión de productos (ADR-004)

Fecha: 2026-09-25

## Modelo LLM utilizado

- opencode / space-bunny-free

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos" (Django 6.1, PostgreSQL, Bootstrap 5, jQuery 4).
- Se solicitó leer e implementar `docs/ADR/adr004-products.md`.
- El módulo products se ubica dentro del monolito modular y mantiene el aislamiento de datos por compañía.

## Objetivo

- Implementar la gestión de productos, consumibles y servicios definida en ADR-004.
- Mantener una solución simple para el MVP, sin implementar un módulo completo de inventario.

## Decisiones tomadas

- Se creó la aplicación Django `products` con un único modelo `Product`.
- `kind` distingue entre `product`, `consumable` y `service`.
- `category` identifica la categoría técnica fotovoltaica.
- `stock_quantity` aplica únicamente a productos; para consumibles y servicios se almacena como `NULL`.
- El stock se valida en la aplicación y no implementa movimientos, reservas, bodegas ni proveedores.
- Se usa `uuid` v4 público e `id` BigAutoField interno.
- Cada producto pertenece a una compañía mediante `ForeignKey` con `PROTECT`.
- La compañía se obtiene desde la compañía creada por el usuario; el staff no puede gestionar productos.
- La eliminación es lógica mediante `deleted_at`.
- Se implementaron operaciones de listar, consultar, crear, editar y eliminar.
- Se reutilizaron `ModalFormMixin`, formularios AJAX, UUID en URLs y `DeleteView` mediante POST.
- Se agregó `technical_specs` como `JSONField`.
- El SKU es único dentro de la compañía mediante validación de formulario.
- Se agregó el enlace de productos a la navegación para usuarios no staff.

## Cambios realizados

### Archivos creados

- `cotizacion/products/`: aplicación Django con modelos, formularios, vistas, URLs, administración, pruebas y templates.
- `cotizacion/products/models.py`: modelo `Product`, opciones de tipo, categoría y unidad, manager/queryset con soft delete.
- `cotizacion/products/forms.py`: formulario CRUD, validación de SKU, stock y especificaciones JSON.
- `cotizacion/products/views.py`: vistas aisladas por compañía con soporte modal.
- `cotizacion/products/urls.py`: rutas del módulo.
- `cotizacion/products/admin.py`: registro administrativo.
- `cotizacion/products/tests.py`: 14 pruebas unitarias y de vistas.
- `cotizacion/products/templates/products/`: templates de lista, formulario modal y detalle.
- `cotizacion/products/migrations/0001_initial.py`: migración inicial.

### Archivos modificados

- `cotizacion/app_config/settings.py`: registro de `products` en `INSTALLED_APPS`.
- `cotizacion/app_config/urls.py`: inclusión de URLs de productos.
- `cotizacion/templates/base.html`: enlace de navegación a productos.

## Problemas encontrados

- Las primeras pruebas de productos duplicaban el error de stock por la validación conjunta del formulario y del modelo.
- El campo `technical_specs` utiliza el mensaje estándar de error JSON de Django, por lo que se ajustó la expectativa de la prueba.
- Se corrigió la visualización de especificaciones técnicas en el detalle para mostrar el valor directamente en lugar de usar `json_script` como contenido visible.

## Dificultades

- No se agregaron tests E2E específicos para productos; las validaciones ejecutadas fueron unitarias y de integración de vistas.

## Pendientes

- Implementar los módulos de cotizaciones que integren elementos de productos, consumibles y servicios, incluyendo la copia histórica de datos comerciales definida en ADR-004.
- Evaluar en una decisión posterior un inventario completo con movimientos, reservas y control de concurrencia.

## Comandos ejecutados

- `python manage.py startapp products`
- `python manage.py makemigrations products`
- `python manage.py check`
- `pytest cotizacion/products/tests.py`
- `pytest`
- `git diff --check`

## Resultado final

- Módulo de productos implementado conforme a ADR-004.
- `python manage.py check` terminó sin errores.
- La suite unitaria completa terminó con 86 pruebas exitosas y 3 pruebas E2E deseleccionadas por la configuración de pytest.
- La aplicación usa la base de datos de test configurada como `test_cotizador`.
