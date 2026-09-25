# Dirección visual del cotizador fotovoltaico

## Propósito

Esta especificación define la dirección visual y de interacción para el cotizador de sistemas fotovoltaicos. Su objetivo es transformar la aplicación en una herramienta comercial clara, precisa y conectada con el trabajo técnico del producto, manteniendo Django, Bootstrap 5, jQuery y el renderizado del lado del servidor.

La interfaz actual funciona como un conjunto de CRUDs de Bootstrap. La propuesta prioriza el flujo central del producto: configurar una compañía, mantener clientes y productos y preparar una cotización comercial.

## Diagnóstico actual

La aplicación ya cuenta con una estructura funcional clara para compañías, clientes, productos y cotizaciones. Sus principales faltantes visuales son:

- navegación global plana, sin estado activo ni contexto de compañía;
- dashboard centrado en la configuración de la compañía, no en la actividad comercial;
- uso uniforme de componentes Bootstrap sin una capa visual propia;
- jerarquía débil en el detalle de cotización;
- estados como texto plano, sin diferenciación visual consistente;
- importes sin suficiente jerarquía ni tratamiento para cifras tabulares;
- tablas extensas sin una respuesta móvil integral;
- estados vacíos que comunican ausencia, pero no explican el siguiente paso;
- Configuración inicial inconsistente cuando todavía no existe una compañía.

## 1. Dirección visual

### Concepto: mesa de ingeniería solar

La aplicación debe sentirse como una mesa de trabajo técnica luminosa, inspirada en planos fotovoltaicos, instrumental de medición y fichas de ingeniería. La dirección evita tanto la estética genérica de un SaaS financiero como la decoración ecológica de una página comercial.

La dirección visual se apoya en:

- fondos claros y neutros;
- líneas finas que evocan la retícula de un panel solar;
- verde fotovoltaico para acciones y resultados positivos;
- amarillo solar para estados que requieren atención;
- azul técnico para información y referencias;
- componentes compactos y precisos;
- densidad visual media-alta;
- una composición general más próxima a una herramienta de ingeniería que a un catálogo promocional.

El detalle de cotización será el elemento más distintivo de la interfaz. Se organizará como una hoja de propuesta técnica, con información de cliente, estado, ítems y total claramente dispuestos. La retícula de un panel solar se utiliza como motivo funcional y contenido, especialmente en estados vacíos, configuración inicial y superficies secundarias.

### Decisiones descartadas

No se propone utilizar:

- fondo oscuro de centro de operaciones;
- verde lima fluorescente;
- fondo crema editorial;
- mosaicos de tarjetas idénticas con sombras suaves;
- gradientes verdes decorativos;
- fotografías de instaladores solares;
- gráficos sin información operativa real;
- cifras gigantes como protagonista permanente.

Estas opciones fueron descartadas porque pueden parecer genéricas, confunden el producto con otras categorías o restan prioridad a las tareas comerciales reales.

## 2. Tipografía

### Familia principal

Se propone **Instrument Sans**, incorporada localmente como recurso estático del proyecto. Se utiliza una sola familia para mantener una jerarquía simple y coherente.

La elección se justifica por su lectura moderna y técnica, su buen rendimiento en tablas densas y su capacidad para funcionar tanto en textos comerciales como en información cuantitativa. La incorporación de la fuente requerirá autorización previa.

### Jerarquía tipográfica

| Uso | Tratamiento |
|---|---|
| Título de página | 32/38 px, peso 650–700, espaciado -0.02em |
| Título de sección | 24/30 px, peso 600–700 |
| Título de tabla o panel | 18/24 px, peso 600 |
| Cuerpo de texto | 16/24 px, peso 400 |
| Navegación, botones y tablas | 14/20 px, peso 500–600 |
| Ayuda y metadatos | 12/16 px, peso 400–500 |

### Reglas

- El ancho de lectura se mantiene entre 65 y 75 caracteres.
- Los textos descriptivos utilizan una interlínea de 1,5.
- Los importes utilizan cifras tabulares mediante `font-variant-numeric: tabular-nums`.
- Las cantidades, precios y totales se alinean a la derecha.
- Los títulos se alinean a la izquierda.
- El centrado se reserva para login, registro y estados vacíos breves.
- No se utilizan mayúsculas sostenidas, versalitas decorativas ni etiquetas nominadas sobre todos los encabezados.
- Los títulos no se decoran con recursos que compitan con su contenido.

## 3. Sistema de colores

### Colores base

| Token | Valor | Uso |
|---|---:|---|
| `paper` | `#F5F7F6` | Fondo general de la aplicación |
| `surface` | `#FFFFFF` | Tablas, formularios y superficies elevadas |
| `ink` | `#17231F` | Texto principal |
| `muted` | `#66736E` | Texto secundario y metadatos |
| `line` | `#D8E0DC` | Bordes y separadores |
| `photovoltaic` | `#176B52` | Acción primaria y confirmación positiva |
| `solar` | `#D9911B` | Atención y preparación |
| `blueprint` | `#DCEEF2` | Información técnica y fondos auxiliares |
| `danger` | `#B23A3A` | Errores y acciones destructivas |

### Estados de cotización

- **Borrador:** gris azulado neutral.
- **Emitida:** azul técnico.
- **Aceptada:** verde photovoltaic.
- **Rechazada:** rojo de error.

Los estados siempre incluyen texto. El color funciona como refuerzo y no como único indicador. Cuando sea necesario, se acompañan con bordes o puntos diferenciados.

### Reglas de accesibilidad

- Los colores principales deben cumplir contraste WCAG AA para su uso previsto.
- El blanco sólo se utiliza sobre el verde primario después de verificar su contraste.
- El amarillo no se utiliza como fondo principal ni como único indicador de estado.
- Las acciones destructivas se distinguen por color, texto y ubicación.
- Los colores de estado no dependen de información exclusiva en un tooltip para ser comprendidos.

La paleta deriva de materiales asociados a la energía solar —vidrio, silicio, cobre y luz— sin caer en una estética decorativa de sostenibilidad.

## 4. Sistema de espaciado

### Escala

La interfaz utiliza una escala base de 4 px.

| Token | Valor | Uso |
|---|---:|---|
| `space-1` | 4 px | Ajuste interno pequeño |
| `space-2` | 8 px | Iconos, texto y controles compactos |
| `space-3` | 12 px | Elementos relacionados |
| `space-4` | 16 px | Relleno de botones, campos y filas |
| `space-5` | 24 px | Relleno de paneles |
| `space-6` | 32 px | Separación de secciones |
| `space-7` | 48 px | Separación de bloques mayores |
| `space-8` | 64 px | Separación excepcional |

### Reglas de composición

- El contenido principal tiene un ancho máximo de 1200 px.
- Los paneles estándar utilizan 24 px de relleno.
- Los campos relacionados se separan entre 16 y 24 px.
- Los encabezados de tabla utilizan 12 px de relleno vertical.
- Las filas de tabla utilizan entre 52 y 60 px de alto en escritorio.
- En móvil, las filas pueden reducirse a 44–48 px sin perder legibilidad.
- Se limita la composición a dos niveles de anidación visual.

La densidad moderada favorece la consulta frecuente de catálogos y cotizaciones sin convertir las pantallas en hojas de cálculo difíciles de leer.

## 5. Modelo de navegación

### Escritorio

La aplicación utiliza una barra lateral fija de 232–240 px.

```text
┌──────────────────────┬─────────────────────────────────────┐
│ Cotizador FV         │ Compañía Solar Sur                   │
│                      │                                     │
│ Resumen              │ Encabezado de sección                │
│ Cotizaciones         │                                     │
│ Clientes             │ Contenido                            │
│ Catálogo             │                                     │
│ Compañía             │                                     │
│                      │                                     │
│ Usuario              │                                     │
│ Cerrar sesión        │                                     │
└──────────────────────┴─────────────────────────────────────┘
```

- La compañía actual permanece visible como contexto global.
- El módulo actual cuenta con estado activo persistente.
- Compañía representa configuración y no la pantalla de inicio.
- Los detalles utilizan breadcrumbs únicamente cuando aportan contexto.
- Las acciones secundarias y destructivas se agrupan en menús contextuales.
- El nombre del usuario y la acción de cerrar sesión permanecen en la zona inferior.

La barra lateral evita el problema de la navegación superior actual, donde Inicio, Clientes, Productos y Cotizaciones tienen el mismo peso y no se indica la pantalla activa.

### Móvil

- Se utiliza una barra superior compacta con la marca y un botón de menú.
- La navegación se presenta en un panel deslizante de Bootstrap.
- Las acciones principales permanecen en el encabezado de cada pantalla.
- Las tablas secundarias pueden convertirse en filas apiladas o grupos de tarjetas.
- La acción principal conserva un ancho y área táctil adecuados.

### Login y registro

Las pantallas públicas utilizan un shell separado, sin navegación de negocio. El objetivo es reducir distracciones y mantener el foco en autenticarse o crear una cuenta.

### Configuración inicial

Cuando el usuario todavía no tiene compañía, la navegación debe conduzlo a una progresión explícita:

```text
Crear compañía → Agregar cliente → Cargar catálogo → Crear cotización
```

Clientes, catálogo y cotizaciones no deben llevar a un error 404 por falta de configuración. El sistema debe indicar qué información falta y ofrecer el siguiente paso.

## 6. Composición del dashboard

El dashboard debe convertirse en un resumen operativo del negocio y no en una tabla adicional de datos de compañía.

### Estructura propuesta

```text
Buenos días, [nombre]
[Crear cotización]                         Compañía: Solar Sur

┌────────────────────────────────────────────────────────────┐
│ En borrador    Emitidas    Aceptadas    Total cotizado      │
│ 4              7           3            $18.450.000         │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────┬───────────────────────────┐
│ Cotizaciones recientes          │ Estado del catálogo       │
│ Cliente   Fecha   Estado  Total │ Clientes       12         │
│ ...                            │ Productos      28         │
│                                │ Sin productos   4         │
│ Ver historial                  │                           │
└────────────────────────────────┴───────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Próximo paso o actividad relevante                          │
└────────────────────────────────────────────────────────────┘
```

### Principios de composición

- Existe una sola acción primaria: “Crear cotización”.
- Los indicadores se agrupan en una franja, no en tarjetas independientes.
- Las cotizaciones recientes siguen un formato tabular compacto.
- El estado del catálogo identifica bloqueos reales del flujo.
- Los datos ausentes muestran `—` y contexto, no ceros falsos.
- Las métricas deben provenir de datos reales de la compañía y respetar el aislamiento establecido.
- Cuando falta la compañía, el dashboard se transforma en una guía de configuración.
- Cuando faltan clientes o productos, las áreas correspondientes ofrecen acciones para resolverlo.

Esta composición responde a las necesidades principales del vendedor: saber qué cotizó, qué propuestas están abiertas y qué impide preparar una nueva cotización.

## 7. Lenguaje visual de los componentes

### Superficies y contenedores

- Bordes de 1 px.
- Radios entre 6 y 10 px.
- Sombras sólo en modales, menús y superficies superpuestas.
- Paneles principales diferenciados mediante borde y contraste de fondo.
- Sin sombras suaves aplicadas indiscriminadamente.

### Botones

- Primario: fondo verde photovoltaic.
- Secundario: borde o fondo neutral.
- Destructivo: rojo y peso visual secundario.
- Terciario: acción de texto.
- Tamaño normal para acciones principales.
- Tamaño pequeño reservado para tablas densas.

Cada pantalla debe presentar una acción primaria evidente. Las acciones destructivas no deben competir visualmente con editar, guardar o crear.

### Tablas

- Encabezados neutros y compactos.
- Filas de 52–60 px en escritorio.
- Nombres de entidad con peso 600 y acceso directo al detalle.
- Acciones agrupadas a la derecha.
- Adaptación real a pantallas pequeñas.
- Importes tabulares y CLP localizado.
- Búsqueda, filtros y paginación cuando el volumen los justifique.

### Formularios

- Labels permanentes.
- Placeholders utilizados sólo como ejemplos, nunca como sustituto del label.
- Errores associados al campo y expresados mediante `aria-invalid`.
- Ayuda contextual debajo de campos complejos.
- Secciones internas: identificación, comercial, inventario y especificaciones.
- Especificaciones técnicas tratadas como información avanzada.
- Acciones al pie, principal a la derecha en escritorio y ancho completo en móvil.

### Estados y mensajes

- Badges sobrios, sin sombras y con texto legible.
- Estados vacíos como orientaciones, no como alertas amarillas genéricas.
- Alertas reservadas para errores o acciones bloqueadas reales.
- Mensajes de éxito conectados a la acción que los originó.
- Errores con causa y siguiente paso cuando sea posible.

### Detalle de cotización

- Cliente, fecha y estado en el encabezado.
- Items presentados como un documento técnico claro.
- Resumen lateral en escritorio con subtotal, total, moneda y estado.
- Total con mayor jerarquía y cifras tabulares.
- En móvil, el resumen aparece después de los items o como bloque visible al continuar.
- Las acciones de edición sólo se muestran cuando la cotización puede modificarse.

## 8. Principios de interacción

### Una acción primaria por pantalla

Cada contexto presenta una acción principal evidente. Esto evita que todas las operaciones compitan con el mismo peso visual.

### Respuesta inmediata

- Los botones muestran estado de carga.
- Se bloquean durante operaciones en curso para evitar duplicados.
- El resultado utiliza el mismo lenguaje de la acción: guardar, crear, editar o eliminar.

### Revelación progresiva

Los campos técnicos y opciones avanzadas permanecen ocultos hasta que sean necesarios. Alta y edición de productos e items deben seguir el mismo patrón.

### Confirmación contextual

Las operaciones destructivas utilizan un diálogo Bootstrap que identifica la entidad y explica la consecuencia. No se utilizan confirmaciones nativas del navegador.

### Estados vacíos accionables

Cada estado vacío explica qué falta y ofrece una acción que desbloquea el flujo. Ejemplos:

- “Agrega un cliente para crear una cotización”.
- “Carga un producto antes de Agregar items”.
- “Configura tu compañía para comenzar”.

### Preservación del contexto

Al cerrar una modal se conserva el foco y la posición de desplazamiento. Las actualizaciones de totales o filas evitan perder el contexto de lectura actual.

### Validación apropiada

- Las reglas básicas se validan en el navegador.
- Las reglas de negocio se validan en Django.
- Los formularios no se envían únicamente para descubrir campos vacíos.
- Los errores permanecen próximos al campo y a la acción afectada.

### Accesibilidad de navegación

- Foco visible.
- Orden lógico de tabulación.
- Modales con foco contenido.
- Ninguna información disponible únicamente por hover.
- Áreas táctiles adecuadas en móvil.

### Movimiento

- Transiciones breves de 120–180 ms.
- Movimiento sólo al abrir, cerrar, guardar o cambiar un estado.
- Respeto de `prefers-reduced-motion`.
- No se utilizan animaciones de entrada para cada tarjeta o sección.

### Adaptabilidad móvil

La experiencia móvil debe conservar legibilidad y acceso a acciones. La adaptación no debe limitarse a comprimir el layout de escritorio.

## Principios transversales

### Claridad antes que decoración

Cada elemento visual debe ayudar a identificar información, jerarquía, estado o próxima acción. Los adornos sin función deben eliminarse.

### Consistencia

Un mismo concepto debe usar el mismo color, nombre, tratamiento y comportamiento en toda la aplicación.

### Orientación comercial

Las acciones y mensajes deben hablar en términos del usuario: “Guardar cotización”, “Agregar producto”, “Crear cliente”. Se evita lenguaje técnico innecesario.

### Especificidad

La interfaz debe mostrar datos reales: estados, fechas, importes y próximos pasos.

## Orden recomendado de evolución

1. Resolver el estado sin compañía y la configuración inicial.
2. Crear el shell con navegación, contexto y estados activos.
3. Convertir el dashboard en un resumen comercial.
4. Priorizar visualmente el flujo de cotización.
5. Normalizar tablas, formularios, modales y estados vacíos.
6. Incorporar búsqueda, filtros y paginación cuando el volumen los justifique.
7. Aplicar la capa visual propia sobre Bootstrap 5.
8. Evaluar responsividad, accesibilidad y contraste.

## Restricciones de implementación

Esta dirección visual no autoriza por sí misma:

- incorporar frameworks de frontend;
- reemplazar Bootstrap o jQuery;
- agregar una SPA o API independiente;
- introducir una librería de gráficos;
- cambiar la arquitectura del proyecto.

La evolución visual debe mantenerse compatible con templates Django, Bootstrap 5, jQuery y CSS propio dentro de los recursos estáticos existentes. Cualquier dependencia nueva, incluida una fuente local, requerirá autorización y justificación.
