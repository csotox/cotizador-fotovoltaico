# ADR-005: Gestión de cotizaciones

## Contexto

El sistema necesita permitir la creación de cotizaciones para clientes de una compañía.

Cada cotización deberá:

* Pertenecer a una compañía.
* Estar asociada a un cliente.
* Contener uno o más productos, consumibles o servicios.
* Permitir indicar la cantidad de cada elemento.
* Calcular automáticamente los subtotales y el total.
* Mantener la información histórica aunque posteriormente cambien los datos del producto.

El objetivo del MVP es disponer de un flujo simple de creación y consulta de cotizaciones, sin implementar todavía impuestos avanzados, descuentos complejos, pagos u órdenes de venta.

---

## Decisión

Se implementará una aplicación Django:

```text
quotations
```

Se utilizarán dos modelos principales:

```text
Quotation
QuotationItem
```

`Quotation` representará la cabecera de la cotización.

`QuotationItem` representará cada producto, consumible o servicio agregado.

---

## Modelo conceptual

```text
quotations

- id
- uuid
- company
- customer
- status
- notes
- total
- created_at
- updated_at
- deleted_at
```

```text
quotation_items

- id
- quotation
- product

- product_name
- product_sku
- unit
- unit_price

- quantity
- subtotal

- created_at
- updated_at
```

---

## Cotización

### `company`

Cada cotización pertenecerá a una compañía.

La compañía será asignada automáticamente según la compañía activa del usuario.

No se mostrará un selector de compañía en el formulario.

### `customer`

Será una `ForeignKey` al cliente.

El cliente deberá:

* Estar activo.
* No estar eliminado.
* Pertenecer a la misma compañía.

La selección del cliente será obligatoria.

### `status`

Se utilizará un campo con estados básicos:

```text
draft
issued
accepted
rejected
```

Las nuevas cotizaciones comenzarán como:

```text
draft
```

Para el MVP, el estado será principalmente informativo.

### `notes`

Campo opcional para observaciones generales.

### `total`

Representará el total de la cotización.

Se almacenará utilizando:

```python
DecimalField
```

El valor será calculado a partir de las líneas de la cotización.

---

## Líneas de cotización

Cada línea pertenecerá a una cotización mediante:

```text
quotation
```

y tendrá asociado un:

```text
product
```

El producto deberá:

* Estar activo.
* No estar eliminado.
* Pertenecer a la misma compañía de la cotización.

---

## Snapshot del producto

Al agregar un producto se copiarán sus principales datos comerciales:

```text
product_name
product_sku
unit
unit_price
```

Estos datos no dependerán posteriormente del registro actual de `Product`.

Esto permitirá conservar correctamente el histórico.

Por ejemplo, si un producto cambia posteriormente de:

```text
$100.000
```

a:

```text
$120.000
```

la cotización antigua deberá mantener:

```text
$100.000
```

---

## Cantidad

Cada línea tendrá:

```text
quantity
```

Se almacenará utilizando:

```python
DecimalField
```

y deberá ser mayor que cero.

Esto permitirá soportar tanto:

```text
2 paneles
```

como eventualmente:

```text
15.5 metros de cable
```

---

## Subtotal

Cada línea calculará:

```text
subtotal = quantity * unit_price
```

Ejemplo:

```text
quantity = 4
unit_price = 120000

subtotal = 480000
```

El usuario no ingresará manualmente el subtotal.

---

## Total de la cotización

El total será:

```text
total = suma de subtotales
```

Ejemplo:

```text
Paneles       $480.000
Inversor      $650.000
Instalación   $300.000

Total       $1.430.000
```

El total deberá recalcularse cada vez que:

* Se agregue una línea.
* Se elimine una línea.
* Se cambie la cantidad.
* Se cambie el producto de una línea.

---

## Flujo de creación

La creación de una cotización seguirá este flujo:

```text
1. Crear cotización
2. Seleccionar cliente
3. Guardar como draft
4. Agregar productos
5. Indicar cantidades
6. Calcular subtotales
7. Calcular total
8. Consultar cotización
```

---

## Interfaz

La vista de edición mostrará:

```text
Cliente
Estado
Notas

Productos
------------------------------------------------
Producto | Cantidad | Precio | Subtotal | Acción
------------------------------------------------

Total
```

El usuario podrá:

```text
Agregar producto
Modificar cantidad
Eliminar producto
```

Los cálculos podrán actualizarse mediante AJAX para evitar recargar completamente la página.

---

## Reglas de negocio

La cotización, cliente y productos deberán pertenecer siempre a la misma compañía.

No se podrán agregar productos:

```text
is_active = False
```

o:

```text
deleted_at != NULL
```

La cantidad deberá ser mayor que cero.

El precio de la línea será obtenido automáticamente desde:

```text
Product.unit_price
```

al momento de agregar el producto.

El usuario no modificará el precio manualmente en el MVP.

---

## Eliminación

Las cotizaciones utilizarán eliminación lógica mediante:

```text
deleted_at
```

Las líneas podrán eliminarse físicamente mientras la cotización permanezca en estado:

```text
draft
```

Para el MVP no se requiere conservar el historial de modificaciones internas de una cotización en borrador.

---

## Operaciones

El módulo permitirá:

```text
Listar cotizaciones
Crear cotización
Consultar cotización
Editar cotización
Agregar productos
Modificar cantidades
Eliminar productos
Eliminar cotización
```

Las URLs públicas utilizarán:

```text
uuid
```

---

## Fuera del alcance del MVP

No se implementarán:

```text
descuentos
IVA configurable
múltiples monedas
vigencia de cotización
condiciones de pago
PDF
envío por correo
firma del cliente
pagos
versionado de cotizaciones
órdenes de venta
reserva de stock
descuento automático de inventario
```

Estas funcionalidades podrán agregarse posteriormente.

---

## Consecuencias

La separación entre:

```text
Quotation
QuotationItem
```

permite manejar una cantidad variable de productos por cotización.

El snapshot de los datos comerciales mantiene correctamente el histórico.

Los subtotales y el total se calculan automáticamente, evitando inconsistencias por ingreso manual.

La solución cubre el flujo principal del MVP:

```text
cliente
+
productos
+
cantidades
+
precios
=
cotización
```
