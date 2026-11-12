# Registro de uso de IA

Registro de las consultas realizadas durante la evaluación, las respuestas resumidas y la adaptación aplicada al proyecto antes de integrar los cambios.las siguientes respuestas se contrastaron con el modelo Django, las plantillas y estilos existentes. Se integraron de forma incremental, adaptando nombres, rutas y validaciones; no se incorporaron fragmentos sin revisar.

## Parte 1

## Consultas y cambios

### 1. Paleta visual inicial

- **Prompt:** «cambia los colores y aspaecto visual de la pagina por colores morados y verdes con detalles en dorado»
- **Resumen de la respuesta:** Propuso renovar la identidad visual usando morado, verde y dorado.
- **Uso y adaptación:** Se ajustaron los tokens de color y los estilos de la interfaz para aplicar la paleta al proyecto.

### 2. Marca y logotipo

- **Prompt:** «cambia el nombre de la ferreteria a Osorno Herramientas y su logo sea un escudo con una vaquita con llaves y engranes»
- **Resumen de la respuesta:** Propuso cambiar el nombre comercial y crear un emblema acorde a la descripción.
- **Uso y adaptación:** Se integró la marca Osorno Herramientas y un logotipo SVG de escudo con vaca, llaves y engranes en las plantillas.

### 3. Ajuste de paleta mediante CSS

- **Prompt textual:** «cambia los colores y aspaecto visual de la pagina por colores morados y verdes con detalles en dorado modifica este codigo de css»
- **Entrada adicional:** La consulta incluía un bloque CSS extenso a partir de `:root` con variables de color y estilos. El bloque suministrado no se reproduce íntegramente en este registro por su extensión.
- **Resumen de la respuesta:** Revisó el CSS compartido y propuso aplicar allí la paleta morada, verde y dorada.
- **Uso y adaptación:** Se adaptaron variables y estilos a la hoja existente, conservando las reglas y componentes que no requerían cambios.

### 4. CRUD de productos desde el sitio

- **Prompt:** «como si fueras un programador seenior implemente las operaciones desde el sitio no solo desde /admin crear un registro con formulario, editar un registro existente y eliminar con confirmación, redirija al listado principal para ver el cambio reflejado desde la BD
- **Uso y adaptación:** Se adaptaron formularios y vistas al modelo `Producto` y al dashboard existente; se añadió una prueba del ciclo CRUD. Se creó el commit `3f66cf7 etapa-1-crud`.

### 5. Reportes con ORM

- **Prompt:** «como desarrollador senior ayudame a crear los reportes con ORM con el Reporte 1, que permita crear un resumen por agrupación: cantidad de registros y algún cálculo por categoría, marca o laboratorio, usando aggregate o annotate del ORM. • para el reporte 2, genera un listado filtrado: registros bajo un umbral (stock crítico, no disponibles, o que requieren receta), usando filter y order_by. • Cada reporte tiene su template, ambos accesibles desde la navegación de base.html, con los cálculos resueltos en la vista con el ORM»
- **Resumen de la respuesta:** Propuso un resumen agrupado por categoría y un reporte de productos con stock crítico.
- **Uso y adaptación:** Se implementaron en las vistas ORM con conteo, precio promedio y stock total; el umbral de stock crítico quedó en 5. Se añadieron plantillas y enlaces en la navegación base.

### 6. Consultas de clientes, validación y sesiones

- **Prompt:** «como desarrollador senior cree el modelo ConsultaCliente (nombre, correo, mensaje, producto de interés opcional, fecha automática), registrado en /admin. • Implemente el formulario con ModelForm, con validaciones campos obligatorios, la vista guarda en la BD y muestra confirmación.»
- **Resumen de la respuesta:** Propuso un modelo y `ModelForm` validados, confirmación de envío, registro en admin y contador de visitas de sesión.
- **Uso y adaptación:** Se creó `ConsultaCliente`, la migración y el formulario; se eligió el contador de visitas al inicio. Se añadieron pruebas de CSRF y de datos inválidos.

### 7. Estilo del formulario de consultas

- **Prompt:** «mejora este formulario acorde a la estetica de la pagina»
- **Resumen de la respuesta:** Recomendó adaptar controles, etiquetas, mensajes y botón a la identidad visual.
- **Uso y adaptación:** Se aplicaron estilos morado-verde-dorado a los campos y al botón, manteniendo el `ModelForm` y sus validaciones.

### 8. Contador de visitas por sesión

- **Prompt:** «Implemente a la pagina una funcionalidad simple cuando inicien sesiones se registren los últimos 3 productos visitados o contador de visitas.»
- **Resumen de la respuesta:** Se eligió el contador de visitas a la página de inicio como funcionalidad de sesión.
- **Uso y adaptación:** Se conservó el contador en la sesión bajo `visitas_inicio` y se verificó junto con CSRF y las validaciones del formulario.


### 9. Dashboard y acceso al panel correcto

- **Prompt:** «mejora el diseño de este apartado acorde al estilo de la pagina y que se pueda acceder a ella desde el boton de panel admin que y existe ya que por error me envia al admin de django»
- **Resumen de la respuesta:** Propuso mejorar el dashboard y corregir el destino del botón de administración.
- **Uso y adaptación:** Se añadieron estilos responsivos al panel personalizado y se enlazó el botón a `admin_dashboard`, no al admin de Django.

### 10. Logo y nombre enlazados al inicio

- **Prompt:** «agrega la funcion de que cuando aprete el logo o el nombre de la tienda desde cualquier modulo me envie al home de la pagina»
- **Resumen de la respuesta:** Recomendó convertir la marca de las plantillas en un enlace al inicio.
- **Uso y adaptación:** Se enlazaron logo y nombre en cabeceras públicas, administrativas y de acceso; se añadieron reglas para conservar su apariencia y pruebas para los módulos.

### 11. Presentación del home

- **Prompt:** «arregla el como se ve el home con todas sus funciones»
- **Resumen de la respuesta:** Identificó que faltaban estilos para varias secciones de la página principal.
- **Uso y adaptación:** Se incorporaron estilos para el hero, navegación, beneficios, categorías, tarjetas, estadísticas y pie de página, con ajustes responsive. Se mantuvieron los accesos, el contador y las acciones existentes.

### 12. Imágenes de las tarjetas de productos

- **Prompt:** «mejora las tarjetas de los productos que las imagenes se centren y se vean completos los articulos con un borde diseñado para contener la imagen y se vea con el estilo acorde de la pagina»
- **Resumen de la respuesta:** Propuso centrar las imágenes, evitar el recorte y crear un marco visual.
- **Uso y adaptación:** Se reemplazó `object-fit: cover` por `contain` y se diseñó un marco con bordes, fondo y tonos dorados. El ajuste se aplicó a las tarjetas del home y del catálogo.

### 13. Carrusel con todos los productos

- **Prompt:** «entre este parte donde dice herramientas que levantan cada obra haya un carrusel elegante y minimalista con todos los articulos que tengo en la tienda y que al seleccionarlos me lleve directamente a el punto de agregar al carrito»
- **Resumen de la respuesta:** Propuso un carrusel horizontal de productos con navegación manual y enlaces al control de compra correspondiente.
- **Uso y adaptación:** Se usó el queryset de productos activos; cada tarjeta enlaza al botón de agregar de ese producto. Se añadieron controles, desplazamiento táctil y una prueba de enlaces.

### 14. Dirección y degradado del carrusel

- **Prompt:** «hace que este carrusel se mueva automaticamente hacia la derecha mostrando los productos y que el el fondo del carrusel sea un color degradado entre verde y morado elegante»
- **Resumen de la respuesta:** Ajustó la dirección del avance y el fondo del carrusel.
- **Uso y adaptación:** Se cambió a avance hacia los productos siguientes cada 3,5 segundos, con un degradado verde-morado y detalles dorados. Se conservó la pausa al interactuar.

### 15. Carrito, continuidad de compra y contador

- **Prompt:** «arregla el carrito de compra acorde el estilo actual y añade la funcion de poder ir agregando articulos al carrito sin tener que estar ingresando en el todo el tiempo y que se vea como una burbuja en rojo con la cantidada de cosas dentro del carrito en standby para su compra»
- **Resumen de la respuesta:** Propuso estilizar el carrito, mostrar la cantidad de unidades en una burbuja roja y permitir seguir agregando sin entrar al carrito.
- **Uso y adaptación:** Se diseñaron las filas de productos y el resumen con la paleta de la tienda. La burbuja se muestra en inicio, catálogo y carrito. Al agregar desde otra página, la vista regresa al referente solo si pertenece al mismo host; se agregó una prueba para rechazar referentes externos.


## Parte 2: Reflexión personal

Durante el desarrollo de Osorno Herramientas utilicé la IA como apoyo para revisar el código y mejorar la presentación de la página.
También me ayudó con correcciones de escritura y con dudas sobre algunas funciones de Django.
Al comienzo le pedí cambiar los colores y la identidad visual de la tienda.
Después fui haciendo consultas más concretas sobre el CRUD, los reportes, las consultas de clientes y el panel administrativo.
Las respuestas que más me sirvieron fueron las relacionadas con cambios puntuales de diseño.
Cuando compartí capturas, me resultó más fácil explicar qué parte de la página quería mejorar.
Las sugerencias de estilo y las correcciones pequeñas me sirvieron como una buena guía inicial.
En cambio, las propuestas que afectaban vistas, sesiones y redirecciones tuve que revisarlas con el código que ya tenía.
No todas las soluciones funcionaron exactamente como esperaba en el primer intento.
Por ejemplo, ajusté el carrusel para que avanzara hacia la derecha y el contador del carrito para que se actualizara sin salir del catálogo.
También comprobé que los cambios no dejaran fuera funciones que ya existían.
Antes de integrar cada ajuste revisé las plantillas, las rutas y el modelo de datos relacionado.
Las pruebas me ayudaron a encontrar diferencias entre lo que pedía y lo que realmente hacía la página.
En este proceso aprendí que una respuesta de IA puede orientar, pero igual hay que entenderla y comprobarla.
También aprendí a describir mejor los problemas, indicando la pantalla y el resultado que buscaba.
En general, la IA me sirvió como apoyo para avanzar, mientras que las decisiones finales y la verificación quedaron vinculadas al proyecto.