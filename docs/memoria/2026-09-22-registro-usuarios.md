# Memoria: Registro de usuarios (accounts)

Fecha: 2026-09-22

## Modelo LLM utilizado

- opencode / big-pickle

## Contexto

- Proyecto "Cotizador de sistemas fotovoltaicos".
- Sesión de trabajo sobre registro de usuarios según ADR-001.

## Objetivo

- Implementar el registro de usuarios (ADR-001) usando `django.contrib.auth`.
- Usar la skill `django-auth`.

## Cambios realizados

### Archivos creados

- `cotizacion/accounts/` (aplicación Django nueva)
  - `forms.py`: `RegistrationForm(UserCreationForm)` con `email` requerido y único (validación en `clean_email`, normalización a minúsculas).
  - `views.py`: `SignUpView` (CreateView) que redirige a `login` con mensaje de éxito; `home` con `@login_required`.
  - `urls.py`: rutas `registro/`, `login/`, `logout/` y raíz `""` para `home`.
  - `tests.py`: 15 tests.
- `cotizacion/templates/base.html`: layout base con Bootstrap 5 (CDN) y bloque de mensajes.
- `cotizacion/accounts/templates/accounts/signup.html`
- `cotizacion/accounts/templates/accounts/login.html`
- `cotizacion/accounts/templates/accounts/home.html`

### Archivos modificados

- `cotizacion/app_config/settings.py`: agregar `accounts` a `INSTALLED_APPS`; `DIRS = [BASE_DIR / 'templates']`; `LOGIN_URL='login'`, `LOGIN_REDIRECT_URL='home'`, `LOGOUT_REDIRECT_URL='login'`.
- `cotizacion/app_config/urls.py`: `include('accounts.urls')` en la raíz.

## Problemas encontrados

- `assertFormError` con la firma antigua (recibía el response) no existe en Django 6.1; se usó la nueva firma con `response.context["form"]`.
- Mensajes de error de Django difieren de los esperados inicialmente (p. ej. "This field is required.", apostrofo tipográfico en el mensaje de contraseñas no coincidentes). Se verificaron los mensajes reales antes de corregir los tests.
- La raíz `/` devolvía 404 porque `home` estaba en `home/`; se movió a la ruta raíz.

## Decisiones tomadas

- Tras registro exitoso: redirigir a `login` (sin auto-login).
- `email` requerido y único, validado a nivel de formulario (sin constraint de BD en el modelo `User` default).
- Crear vista `home` simple como destino autenticado (`LOGIN_REDIRECT_URL`).
- Incluir login/logout como soporte del flujo.
- No se crea empresa ni rol al registrarse (alineado con ADR-001 y el modelo SaaS).

## Dificultades

- Ninguna relevante.

## Pendientes

- Unicidad de email sin constraint de BD (condición de carrera posible). Si se decide, adoptar usuario personalizado (`AbstractUser` con `email` único) requeriría nuevo ADR.
- Vista `home` provisional; su contenido final depende del módulo de cotizaciones del MVP.
- Bootstrap 5 mediante CDN (depende de conectividad).
- Convención de idioma de las URLs en español no documentada.
- Sin confirmación por email en MVP.

## Comandos ejecutados

- `python ./cotizacion/manage.py startapp accounts cotizacion/accounts`
- `python ./cotizacion/manage.py check` (sin issues)
- `python ./cotizacion/manage.py test accounts` (15/15 OK)

## Resultado final

- Registro de usuarios implementado y validado. Acceso a `/` redirige a login; después de autenticarse queda en `/`.