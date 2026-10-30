# Edición de producto · 29 de octubre de 2026

La página de entrada presenta la obra como un producto editorial: una propuesta clara, tres recorridos de lectura, una demostración breve y una descarga completa. La referencia a una presentación de producto no implica afiliación a Y Combinator, financiación ni métricas de uso.

## Decisión visual

Papel `#ecece2`, tinta vegetal `#25372a`, noche `#111613`, musgo `#b7c398` y oro discreto. Tipografía serif del sistema para la voz literaria, sans serif para explicar y monoespaciada para identificar las láminas. SVG originales con geometría proyectada, sin dependencias externas; no son escenas WebGL ni diagramas científicos.

El descubrimiento recomendado empieza por la ficción, continúa por el razonamiento filosófico y regresa a las prácticas. La numeración original del libro permanece intacta. Los nueve símbolos originales se conservan; se añaden cuatro láminas y una composición de portada.

## Mapa de fuentes y adaptación

| Experiencia | Fuente del libro | Adaptación |
| --- | --- | --- |
| Promesa y límites de lectura | `capitulos/portada.md` | Entrada revisada: distingue compromisos éticos, afirmaciones factuales y exploración metafísica. |
| Nombre de Dios | `capitulos/el-nombre-de-lo-posible.md` | El lenguaje teológico se presenta como propuesta interpretativa. |
| Incógnita abierta | `capitulos/lo-que-el-libro-no-decide.md` | La falta de una explicación no prueba una causa sobrenatural. |
| Laboratorio: imaginar | `capitulos/el-hambre-en-la-abundancia.md` | Ejemplo original de ciudad sin hambre; posibilidad narrativa, no pronóstico. |
| Laboratorio: filosofar | `capitulos/los-cuatro-universales.md` | Quién decide, a quién se excluye, quién responde: preguntas morales. |
| Laboratorio: contrastar | `capitulos/la-asamblea-de-verificacion.md` | Esbozo de comprobación, sin datos inventados ni resultados empíricos. |
| Laboratorio: dejar abierto | `capitulos/lo-que-el-libro-no-decide.md` | Pregunta sobre propósito; ninguna respuesta se presenta como probada. |
| Atlas interactivo | `capitulos/los-simbolos.md`, `simbolos/*.svg` | Descripciones breves de prácticas, con descarga del SVG original. |

El laboratorio es una introducción editorial, no un motor capaz de verificar afirmaciones. Los anillos cambian para identificar la etapa seleccionada. Su rotación es simbólica: no codifica cantidades, probabilidades o evidencia.

## Método Taster

Se consultó `/Users/josoroma/sites/taster/SKILL.md` y `references/interactive-books.md`. Se adaptó `createTransport` de `kit/motion.mjs` a un script clásico para conservar `file://`. Su licencia se distribuye en `web/assets/vendor/TASTER-LICENSE.txt`. Los recursos del proyecto funcionan de forma independiente.

La animación empieza solo al pulsar «Animar símbolo». Permite pausar, buscar una posición y restablecer. Se pausa al ocultar la pestaña, salir de la figura o cambiar la preferencia de movimiento reducido. Las pestañas del laboratorio admiten flechas, Inicio y Fin. El atlas y la pregunta de comprobación ofrecen resultados legibles; todo el libro sigue disponible en HTML estático sin JavaScript.

## Formatos y audio

`index.html` es la presentación; `web/index.html`, el lector; `web/completo.html`, el texto íntegro para lectura e impresión. El ZIP incluye fuentes, texto e imágenes y desactiva las peticiones de audio. Se omiten los MP3 para mantener la descarga ligera. Las grabaciones online de 00, 02 y 08 se desactivan por su revisión editorial; deben regenerarse y retirarse de `web/audio-pendiente.json` antes de volver a mostrarlas.

## Verificación realizada

- Reconstrucción de 36 entradas y validación de enlaces locales, continuidad de capítulos, imágenes y estado del audio.
- Extracción real del ZIP, nueva comprobación de sus rutas e integridad del archivo.
- 55 comprobaciones en jsdom sobre el HTML y JavaScript reales: pestañas, teclado, explicación de respuestas, nueve descargas, búsqueda, tema, navegación, menú, pausa, posición exacta y reinicio del transporte.
- Inspección visual de los SVG mediante renderizado nativo de Quick Look y validación XML.
- Respuesta HTTP 200 de la página servida localmente.

La conexión de navegador no estuvo disponible y el acceso nativo a Edge agotó el tiempo de espera. No se verificaron en navegador el diseño final, la disposición móvil, la reproducción de audio ni la consola. Las comprobaciones DOM no equivalen a una prueba visual. Esta edición se preparó localmente; no se realizó un despliegue remoto.
