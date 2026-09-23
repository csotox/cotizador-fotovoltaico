# ADR-002: Gestión de compañias

## Contexto

Dentro del modelo SAAS las compañias son las empresas asociadas al usuario y que son las encargadas de generar las cotizaciones.

El sistema debe permitir que un usuario registrado pueda crear la empresa que emitira las cotizaciones.

La empresa debe quedar asociada al usuario que la ha creado.

## Decisión

- Debe ser una App de Django.
- Un usuario que es Staff no puede crear una empresa.

## Consecuencias

## Modelo conceptual

### Compañias

Modelo de Compañias. Representa la empresa que genera la cotización.

```text
companies
- id
- idx
- name
- alias
- direccion
- rut
- email
- created_at
- updated_at
- deleted_at
```
