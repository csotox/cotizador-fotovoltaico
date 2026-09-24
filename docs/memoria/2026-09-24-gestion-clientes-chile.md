# Memoria: gestión de clientes y contexto Chile

- Modelo LLM: space-bunny-free.
- Contexto: El sistema opera para Chile y se implementó la gestión de clientes.
- Objetivo: Documentar el contexto chileno, registrar ADR-003 e implementar clientes dentro del modelo SaaS.
- Cambios realizados: Se actualizaron `docs/product.md`, `docs/arquitecture.md` y `docs/domin.md`; se creó `docs/ADR/adr003-customers.md`; se agregó la app `customers` con modelo, catálogo chileno, formularios, vistas, URLs, templates, admin y pruebas; se conectó la navegación; se activó la regla de una compañía activa por usuario en software; se configuraron `es-CL` y `America/Santiago`; se generaron las migraciones de clientes.
- Problemas encontrados: El cambio de idiomamfumó expectativas de mensajes en inglés en pruebas existentes; se actualizaron. El catálogo inicial no estaba conectado al campo `commune`; se conectó y generó una migración.
- Decisiones tomadas: Cliente con `id` interno, `uuid` público, compañía automática, soft delete, email único por compañía validado en formulario, comuna como referencia chilena y forma de pago como lista fija. No se incluye número de cuenta. No se agrega restricción de compañía única en base de datos.
- Dificultades: La suite existente usaba mensajesingleses y datos de prueba con RUT repetido; ambos se ajustaron.
- Pendientes: Producto y cotizaciones siguen fuera de esta implementación. El catálogo de comunas entregado es un subconjunto curado y puede ampliarse.
- Comandos ejecutados: `python manage.py makemigrations customers`; `python manage.py check`; `pytest customers/tests.py companies/tests.py`; `pytest`; `pytest -m e2e`.
- Resultado final: `check` sin errores; 72 pruebas no E2E aprobadas y 3 E2E aprobadas contra `test_cotizador`.
