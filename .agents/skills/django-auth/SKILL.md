---
name: django-auth
description: Implementa y revisa funcionalidades de autenticación y autorización usando las herramientas nativas de Django.
---

# Django Auth

## Objetivo

Implementar funcionalidades relacionadas con usuarios, autenticación y autorización utilizando las herramientas nativas de Django.

## Antes de implementar

Revisar:

- `docs/product.md`
- `docs/domain.md`
- `docs/architecture.md`
- ADR relacionados con usuarios, empresas, roles o permisos.

No generar reglas de negocio que no estén documentadas.

## Reglas generales

- Utilizar `django.contrib.auth`.
- No implementar almacenamiento manual de contraseñas.
- No guardar contraseñas en texto plano.
- Utilizar los mecanismos de hashing de Django.
- Utilizar protección CSRF en formularios.
- Utilizar las utilidades de autenticación proporcionadas por Django.
- No crear un sistema de autenticación personalizado salvo que exista una decisión documentada que lo requiera.
- No utilizar `is_superuser` para representar administradores de una empresa SaaS.
- Mantener separados los permisos globales del sistema y los permisos dentro de una empresa.

## Registro de usuario

Al implementar registro:

- Validar los datos de entrada.
- Utilizar los mecanismos de creación de usuarios de Django.
- Evitar duplicación de usuarios según las reglas definidas por el proyecto.
- Después del registro, seguir únicamente el flujo definido en los requisitos.

## Login

Al implementar inicio de sesión:

- Utilizar `authenticate()`.
- Utilizar `login()`.
- Respetar usuarios inactivos.
- No revelar si un usuario específico existe mediante mensajes de error innecesariamente detallados.

## Logout

Al implementar cierre de sesión:

- Utilizar `logout()`.
- Invalidar correctamente la sesión actual.

## SaaS

La autenticación de un usuario y su pertenencia a una empresa son conceptos distintos.

No debe asumir:

- Que todo usuario tiene una empresa.
- Que un usuario pertenece a una sola empresa.
- Que registrarse crea automáticamente una empresa.
- Que registrarse convierte al usuario en administrador de una empresa.

## Validación

Después de implementar:

- Ejecutar `python manage.py check`.
- Ejecutar las pruebas relacionadas.
- Informar archivos modificados y validaciones ejecutadas.
