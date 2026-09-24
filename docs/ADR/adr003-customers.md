# ADR-003: Gestión de clientes

## Contexto

El sistema está diseñado para operar en Chile y el modelo SaaS establece que cada registro de negocio pertenece a una compañía. En el contexto del producto, una compañía es la organización que emite cotizaciones; un cliente puede ser una persona natural o una persona jurídica (una empresa receptora de la cotización).

Cada usuario no staff puede tener una sola compañía activa como regla de negocio, sin agregar una restricción a nivel de base de datos. Dentro de esa compañía se deben registrar clientes con la información mínima necesaria para contacto y cotización: nombre, dirección, email, teléfono, comuna chilena y forma de pago.

La forma de pago es un dato comercial del cliente y no implica procesamiento de pagos, que permanece fuera del MVP.

## Decisión

- Se implementará una aplicación Django `customers`.
- Los nombres de las columnas se definirán en inglés: `name`, `address`, `email`, `phone`, `commune` y `payment_method`.
- Cada cliente tendrá un identificador `uuid` público y un `id` autoincremental interno, según la convención del proyecto.
- Cada cliente pertenecerá a una compañía. El usuario no staff tendrá una sola compañía activa, por lo que el cliente se asignará automáticamente a ella y no se expondrá un selector de compañía en el formulario.
- La regla de una sola compañía activa se validará en la aplicación mediante el formulario o la vista de creación. No se agregará una restricción de unicidad a nivel de base de datos.
- El personal staff no podrá gestionar clientes desde las vistas web.
- La comuna se almacenará como un `CharField` con opciones de un catálogo de comunas chilenas agrupadas por región. El catálogo será un dato de referencia del sistema, no un modelo de negocio.
- La forma de pago será una lista fija de opciones chilenas: efectivo, transferencia bancaria, cheque, tarjeta de débito, tarjeta de crédito y letras de cambio.
- Se ofrecerán las operaciones de registrar, editar, consultar y eliminar clientes. La eliminación será lógica mediante `deleted_at`.
- Las vistas reutilizarán el patrón de `companies`: `ModalFormMixin`, UUID en URLs, formularios AJAX, mensajes de éxito y `DeleteView` limitado a POST.
- El email se normalizará a minúsculas y se validará como único dentro de la compañía en el formulario, excluyendo la instancia editada y los clientes eliminados lógicamente.

## Consecuencias

- La información de clientes queda aislada por compañía mediante filtros de queryset y relaciones del modelo.
- La regla de compañía activa única es una regla de negocio de la aplicación y puede cambiar en el futuro sin modificar el esquema de base de datos.
- El UUID se utiliza en las URLs y el `id` interno no se expone en formularios, URLs ni interfaces.
- La eliminación lógica conserva el historial de clientes y permite la recuperación futura.
- El catálogo de comunas se mantiene como referencia de la aplicación y no requiere una tabla de base de datos.
- La forma de pago queda registrada como preferencia comercial, sin implementar pagos.
- La unicidad de email entre clientes no está garantizada por una restricción de base de datos y depende de la validación del formulario.
- El teléfono y el email se almacenarán normalizados por los formularios para facilitar la consistencia.
- La terminología documentada distingue la compañía emisora del cliente empresa, que puede ser una persona jurídica.
