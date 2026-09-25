# ADR-004: Gestión de productos

## Contexto

El sistema necesita gestionar los elementos que pueden incluirse en una cotización fotovoltaica.

Cada compañía deberá poder registrar tres tipos:

* **Producto**: bien físico, por ejemplo paneles, inversores o baterías.
* **Consumible**: material utilizado durante una instalación, por ejemplo cables o conectores.
* **Servicio**: trabajo o mano de obra, por ejemplo instalación o puesta en marcha.

El catálogo debe pertenecer a una compañía y respetar el aislamiento de datos del modelo SaaS.

Para el MVP se requiere una solución simple, evitando implementar un sistema completo de inventario.

---

## Decisión

Se implementará una aplicación Django:

```text
products
```

Se utilizará un único modelo:

```text
Product
```

con un campo:

```text
kind
```

con los valores:

```text
product
consumable
service
```

---

## Clasificación técnica

Se incorporará además un campo:

```text
category
```

para identificar el tipo técnico del elemento.

Valores iniciales:

```text
solar_panel
inverter
battery
mounting_structure
cable
connector
installation
engineering
other
```

Ejemplo:

```text
Panel JA Solar 550 W

kind = product
category = solar_panel
```

```text
Cable solar 6 mm²

kind = consumable
category = cable
```

```text
Servicio de instalación

kind = service
category = installation
```

---

## Modelo conceptual

```text
products

- id
- uuid
- company

- kind
- category

- name
- description
- sku

- manufacturer
- model

- unit_price
- unit
- stock_quantity

- technical_specs

- is_active

- created_at
- updated_at
- deleted_at
```

---

## Campos principales

### `id`

`BigAutoField` interno.

No se expondrá públicamente.

### `uuid`

`UUIDField` v4, único y no editable.

Se utilizará en URLs.

### `company`

`ForeignKey` a `Company`.

```python
on_delete=models.PROTECT
```

El producto pertenecerá siempre a una compañía.

### `kind`

`CharField` con las opciones:

```text
product
consumable
service
```

### `category`

`CharField` con opciones controladas para identificar la categoría técnica.

### `name`

Nombre del elemento.

Obligatorio.

### `description`

Descripción opcional.

### `sku`

Código interno opcional.

Cuando exista, deberá ser único dentro de la compañía.

### `manufacturer`

Fabricante del producto.

Opcional.

### `model`

Modelo comercial o técnico.

Opcional.

### `unit_price`

Precio unitario en CLP.

Se almacenará utilizando:

```python
DecimalField
```

### `unit`

Unidad de venta.

Valores iniciales:

```text
unit
meter
square_meter
hour
day
service
```

### `stock_quantity`

Cantidad disponible.

Será:

```python
PositiveIntegerField
```

nullable.

Solo aplicará cuando:

```text
kind = product
```

Para consumibles y servicios será:

```text
NULL
```

El stock será gestionado manualmente en el MVP.

### `technical_specs`

Se utilizará:

```python
JSONField
```

para almacenar especificaciones técnicas básicas cuando sean necesarias.

Ejemplo para un panel:

```json
{
  "rated_power_w": 550,
  "voc_v": 49.9,
  "isc_a": 13.9
}
```

Ejemplo para un inversor:

```json
{
  "rated_ac_power_w": 5000,
  "max_dc_voltage_v": 600,
  "mppt_count": 2
}
```

No será obligatorio para todas las categorías.

### `is_active`

`BooleanField` con valor predeterminado:

```text
True
```

Los elementos inactivos no podrán utilizarse en nuevas cotizaciones.

### `created_at`

Fecha de creación.

### `updated_at`

Fecha de última modificación.

### `deleted_at`

Fecha de eliminación lógica.

---

## Reglas de negocio

Cada producto deberá pertenecer a la compañía activa del usuario.

El usuario no podrá seleccionar manualmente una compañía desde el formulario.

Las consultas deberán filtrar siempre por compañía.

Los registros eliminados mediante `deleted_at` no deberán aparecer en las consultas normales.

Cuando:

```text
kind = product
```

se permitirá utilizar:

```text
stock_quantity
```

Cuando:

```text
kind = consumable
kind = service
```

`stock_quantity` deberá ser:

```text
NULL
```

Si se cambia el tipo de un elemento, deberán limpiarse los valores que ya no correspondan.

---

## Operaciones

El módulo permitirá:

```text
Listar
Consultar
Crear
Editar
Eliminar
```

La eliminación será lógica.

Las vistas utilizarán los patrones ya existentes del proyecto:

```text
UUID en URLs
formularios AJAX
ModalFormMixin
mensajes de éxito
DeleteView mediante POST
```

---

## Uso en cotizaciones

Una cotización podrá utilizar elementos que:

```text
is_active = True
deleted_at = NULL
```

y pertenezcan a la misma compañía.

La línea de cotización deberá almacenar una copia de los datos comerciales utilizados al momento de cotizar.

Como mínimo:

```text
product
product_name
unit
unit_price
quantity
```

Esto evita que una cotización histórica cambie si posteriormente se modifica el precio o nombre del producto.

---

## Fuera del alcance del MVP

No se implementarán:

```text
movimientos de inventario
reservas de stock
bodegas
proveedores
órdenes de compra
historial de precios
alertas de stock
números de serie
validaciones automáticas SEC
dimensionamiento automático
compatibilidad entre equipos
```

Estas funcionalidades deberán evaluarse en decisiones arquitectónicas posteriores.

---

## Consecuencias

El modelo único simplifica formularios, vistas y consultas.

`kind` define el comportamiento comercial del elemento.

`category` define su función dentro de la instalación fotovoltaica.

`technical_specs` permite almacenar información técnica básica sin crear modelos separados para paneles, inversores o baterías.

La solución cubre las necesidades mínimas del MVP y mantiene una estructura extensible para futuras funcionalidades.
