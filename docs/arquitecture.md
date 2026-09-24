# Arquitectura del proyecto

## Estilo de arquitectura

- Aplicación monolito modular construido con Django.
- Renderizado del lado del servidor.
- PostgreSQL como base de datos principal.
- Bootstrap 5 para la UI.
- jQuery para interacciones simples en el frontend.

## Modelo SaaS
- Base de datos compartida.
- Los datos deben estar aislados por empresa.
- Cada registro de negocio debe pertenecer a una empresa.
- Un usuario solo puede acceder a información de las empresas a las que pertenece.

## Contexto chileno
- El sistema está diseñado para operar en Chile.
- La configuración regional debe utilizar español de Chile (`es-CL`) y la zona horaria `America/Santiago`.
- Las montos y cotizaciones se expresarán en pesos chilenos (CLP).
- Los RUT se validarán según el formato y algoritmo chileno.
- Las comunas se gestionarán mediante un catálogo de referencia chileno.
- Una compañía es la organización que emite cotizaciones; una empresa puede ser un cliente persona jurídica.


## Módulos principales (Aplicaciones Django)

- `accounts`
  - Usuarios.
  - Autenticación.
  - Autorización.

- `companies`
  - Empresas.
  - Relación entre usuarios y empresas.

- `customers`
  - Clientes de cada empresa.

- `products`
  - Productos y componentes fotovoltaicos.

- `quotations`
  - Cotizaciones.
  - Detalle de productos cotizados.
  - Cálculos y totales.

## Principios

- Utilizar el ORM de Django.
- Utilizar migraciones para cambios de base de datos.
- No colocar lógica de negocio en los templates.
- Mantener las vistas lo más simples posible.
- Separar presentación, lógica de negocio y persistencia.
- Evitar dependencias externas innecesarias.
- No incorporar nuevas tecnologías sin justificar su necesidad.
- Toda consulta de información de negocio debe respetar el aislamiento por empresa.

## Alcance inicial

La arquitectura debe mantenerse simple y orientada al MVP.

No se implementarán inicialmente:

- Aplicación SPA.
- API REST independiente.
- Colas de procesamiento.
- Microservicios.
- Servicios distribuidos.
