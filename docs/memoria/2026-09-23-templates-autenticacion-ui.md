# Memoria: Templates de autenticación con Bootstrap 5 (system-ui)

Fecha: 2026-09-23

## Modelo LLM utilizado

- opencode / big-pickle

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos".
- Sesión de trabajo sobre los templates de autenticación existentes (`login`, `signup`, `home`) usando la skill `system-ui`.

## Objetivo

- Revisar todos los templates de autenticación.
- Asegurar uso de Bootstrap 5, plantilla base común y diseño consistente.
- No cambiar la lógica de autenticación.
- Preparar la estructura para reutilizar el mismo diseño en templates futuros.
- Generar y ejecutar un plan de implementación.

## Cambios realizados

### Archivos modificados

- `cotizacion/templates/base.html`:
  - Bloques `{% block extra_css %}` y `{% block extra_js %}` para extensión futura.
  - Mapeo de `message.tags`: tag `error` se renderiza como `alert-danger` en vez de `alert-error`.

- `cotizacion/accounts/templates/accounts/login.html` y `signup.html`:
  - Refactorizados para extender el partial `_auth_card.html` e incluir `_form_fields.html`.
  - Se mantienen URLs, names de campos, `csrf_token`, botones y enlaces cruzados.

- `cotizacion/accounts/forms.py`:
  - Nuevo `LoginForm(AuthenticationForm)`.
  - `LoginForm` y `RegistrationForm` aplican `class="form-control"` a todos los widgets en `__init__`.

- `cotizacion/accounts/urls.py`:
  - `login/` ahora usa `authentication_form=LoginForm`.

### Archivos creados

- `cotizacion/accounts/templates/accounts/partials/_auth_card.html`:
  - Extiende `base.html`; card centrado (`col-md-6 col-lg-5`) con bloques `auth_title` y `auth_body`. Base reutilizable para templates de auth y futuros flujos (p. ej. reset de contraseña).

- `cotizacion/accounts/templates/accounts/partials/_form_fields.html`:
  - Renderiza `form.non_field_errors`, labels, inputs (`{{ field }}`), errores por campo y `help_text`.

### Archivos eliminados

- `cotizacion/accounts/templatetags/` (contenía `prettify.py` con el filtro `addclass`).

## Problemas encontrados

- Al visitar `http://localhost:8000/login/?next=/` el usuario reportó un error relacionado con la librería `prettify`. En un intérprete fresco el render funcionaba (15/15 tests OK, GET `/login/?next=/` responde 200), por lo que el error se atribuyó a caché vieja del autoreloader de `runserver`.

## Decisiones tomadas

- Aplicar clases de Bootstrap desde `forms.py` (`widget.attrs["class"] = "form-control"`) en lugar de un filtro de templates, tras consulta con el usuario («Eliminar prettify, estilar en forms.py»).
- La presentación queda en `forms.py`/templates; no se modificó lógica de autenticación.
- Se descartó `crispy-forms`/`widget_tweaks`: sin autorización no se agregan dependencias.

## Dificultades

- El error de `prettify` no es reproducible en un intérprete limpio; se resolvió eliminando la librería solicitada por el usuario.

## Pendientes

- Verificar en navegador que `http://localhost:8000/login/?next=/` y `/registro/` rendericen correctamente tras reiniciar `runserver` (validaciones automáticas ya pasan).
- Templates del resto del MVP deben reutilizar `base.html` y los partials creados.

## Comandos ejecutados

- `python manage.py check` (sin issues)
- `python manage.py test accounts` (15/15 OK)
- Verificación de renderizado con `django.test.Client`: `/login/?next=/` y `/registro/` responden 200, contienen `form-control` y no referencian `prettify`.

## Resultado final

- Templates de autenticación consistentes con Bootstrap 5 sobre `base.html`, con partials reutilizables y estilos de inputs aplicados desde `forms.py`. Sin cambios en la lógica de autenticación. Validaciones automáticas aprobadas.