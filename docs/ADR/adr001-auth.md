# ADR-001: Autenticación de usuarios

## Contexto

El sistema necesita permitir que los usuarios se registren, inicien sesión y cierren sesión.

La aplicación es un SaaS y posteriormente cada usuario podrá asociarse a una empresa.

## Decisión

Se utilizará el sistema de autenticación nativo de Django.

- `django.contrib.auth`
- Formularios y utilidades de autenticación de Django.
- Contraseñas gestionadas mediante el sistema de hashing de Django.
- Sesiones gestionadas por Django.

No se implementará un sistema de autenticación personalizado salvo que exista una necesidad futura documentada.

## Consecuencias

- Se reutilizan mecanismos estándar de Django.
- La autenticación queda separada de los permisos propios de cada empresa.
- Los roles de empresa no utilizarán `is_superuser` como mecanismo de autorización.
