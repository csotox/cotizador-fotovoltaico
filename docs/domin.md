# Dominio del proyecto

## Empresa o compañía

Representa a la organización que utiliza el sistema y emite las cotizaciones. En este documento se conserva el nombre técnico `Company`; el nombre de negocio preferred es **compañía** para diferenciarla de una empresa que puede ser cliente.

Responsabilidades:

- Ser propietaria de sus datos.
- Tener usuarios asociados.
- Tener clientes.
- Tener productos.
- Tener cotizaciones.

Relaciones:

- Una compañía puede tener varios usuarios.
- Una compañía puede tener varios clientes.
- Una compañía puede tener varios productos.
- Una compañía puede tener varias cotizaciones.
- Un usuario no staff puede tener una sola compañía activa como regla de negocio.

---

## Usuario

Representa a una persona que utiliza el sistema.

Responsabilidades:

- Autenticarse.
- Acceder solamente a empresas autorizadas.
- Ejecutar acciones según sus permisos.

Relaciones:

- Un usuario puede pertenecer a una o más empresas.

---

## Cliente

Representa al cliente final que solicita una cotización fotovoltaica.

Responsabilidades:

- Identificar a la persona o empresa cotizada.
- Mantener sus datos comerciales básicos.

Relaciones:

- Un cliente pertenece a una empresa.
- Un cliente puede tener varias cotizaciones.

---

## Producto

Representa un componente que puede formar parte de una solución fotovoltaica.

Ejemplos:

- Panel solar.
- Inversor.
- Batería.
- Estructura.
- Protecciones.
- Mano de obra.
- Otros componentes.

Responsabilidades:

- Representar un elemento cotizable.
- Mantener información comercial necesaria para una cotización.

Relaciones:

- Un producto pertenece a una empresa.
- Un producto puede aparecer en múltiples cotizaciones.

---

## Cotización

Representa una propuesta comercial realizada para un cliente.

Responsabilidades:

- Asociar una propuesta a un cliente.
- Mantener los productos y servicios cotizados.
- Calcular subtotales y total.
- Mantener su información histórica.

Relaciones:

- Una cotización pertenece a una empresa.
- Una cotización pertenece a un cliente.
- Una cotización contiene uno o más ítems.

---

## Ítem de cotización

Representa una línea dentro de una cotización.

Responsabilidades:

- Indicar qué producto fue cotizado.
- Mantener cantidad y precio utilizado.
- Calcular su subtotal.

Relaciones:

- Un ítem pertenece a una cotización.
- Un ítem puede estar asociado a un producto.
