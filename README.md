# El Libro de lo Posible

![El Libro de lo Posible: imaginación primero, filosofía después](web/assets/art/cover.svg)

**Imagina otros futuros. Aprende a discutirlos.**

Un libro interactivo en español para pensar por cuenta propia en la era de las inteligencias artificiales. Combina una ficción sobre una ciudad que dejó de preguntar, una propuesta filosófica y prácticas para tomar decisiones sin entregar el criterio a un oráculo.

[**Explorar el libro →**](https://josoroma.github.io/el-libro-de-lo-posible/) · [Leer el relato](web/index.html#el-dia-en-que-dejamos-de-preguntar) · [Descargar la edición](releases/el-libro-de-lo-posible.zip)

> Nada verdadero exige obediencia; nada posible exige permiso.

## La idea

Tenemos herramientas que responden cada vez más preguntas. Este libro explora cómo conservar la capacidad de formular las nuestras, contrastar las respuestas y asumir lo que decidimos.

La experiencia empieza por la imaginación: una puerta, un símbolo, un futuro posible. Después vienen las preguntas filosóficas. Cuando una idea afirma algo sobre el mundo, pide evidencia. La estética puede ser esotérica; el criterio para aceptar una explicación sigue siendo racional.

**No saber es un punto de partida, no una prueba de lo sobrenatural.** Hay espacio para la metafísica como exploración abierta, con sus supuestos a la vista. Una ficción no demuestra una predicción; una elección moral no se convierte en ley natural por llamarla universal.

## Para quién

- Lectores de ciencia ficción que quieren discutir las ideas detrás de la historia.
- Personas que crean o utilizan inteligencia artificial y quieren examinar el poder que le delegan.
- Grupos de lectura que buscan preguntas, desacuerdos claros y prácticas que puedan revisar juntos.

## Empieza por una experiencia

| Si quieres… | Empieza aquí | Qué encontrarás |
|---|---|---|
| Imaginar un mundo diferente | [Los Últimos Universales](web/index.html#el-dia-en-que-dejamos-de-preguntar) | Áncora confió sus decisiones a una inteligencia. Algunas personas vuelven a preguntar. |
| Examinar los argumentos | [Los cuatro universales](web/index.html#los-cuatro-universales) | Realidad, Persona, Responsabilidad y Reciprocidad como marco filosófico y ético. |
| Probar una práctica | [Ritual del Umbral](web/index.html#ritual-del-umbral) | Separar lo observado, lo supuesto y lo desconocido antes de decidir. |
| Explorar el límite del conocimiento | [Lo que este libro no decide](web/index.html#lo-que-el-libro-no-decide) | Metafísica abierta y una distinción explícita entre incertidumbre y explicación. |
| Llevarlo a una conversación | [La Asamblea de Lectura](web/index.html#la-asamblea-de-lectura) | Una lectura compartida donde nadie posee la interpretación. |

## Qué incluye

**Una portada y 35 capítulos, organizados en tres partes:**

| Parte | Capítulos | Función |
|---|---|---|
| I · El Libro de lo Posible | 01–12 | La propuesta: cuatro universales, límites del poder, instituciones y apertura metafísica. |
| II · El Camino Práctico | 13–21 | Siete prácticas, una asamblea y un calendario para volver a lo que importa. |
| III · Los Últimos Universales | 22–35 | El relato de Áncora, sus inteligencias y las personas que recuperan la costumbre de comprobar. |

La portada es la entrada 00. El [índice completo](indice.md) enlaza las 36 entradas y sus resúmenes.

La edición reúne una página de presentación con un laboratorio interactivo de ideas, ilustraciones por sección, nueve símbolos originales en SVG y varias formas de leer. No hace falta una cuenta.

| Formato | Archivo | Uso |
|---|---|---|
| Presentación interactiva | [index.html](index.html) | Descubrir el libro, explorar sus ideas y elegir una ruta de lectura. |
| Lector por capítulos | [web/index.html](web/index.html) | Índice, búsqueda, progreso, tema claro/oscuro y audio disponible por capítulo. |
| Libro completo | [web/completo.html](web/completo.html) | Leer sin JavaScript, imprimir o guardar como PDF desde el navegador. |
| Texto editable | [OBRA-COMPLETA.md](OBRA-COMPLETA.md) | La obra unificada en Markdown. |
| Galería | [web/simbolos/index.html](web/simbolos/index.html) | Los nueve símbolos y su significado. |
| Edición descargable | [el-libro-de-lo-posible.zip](releases/el-libro-de-lo-posible.zip) | Sitio, texto, ilustraciones, símbolos y fuentes para abrirlos localmente; sin MP3. |

Los símbolos son recursos de imaginación y memoria. No representan fuerzas ocultas ni se presentan como evidencia. Las prácticas son ejercicios de reflexión, no tratamientos clínicos.

El ZIP es una edición ligera de texto e imágenes. El lector incluido desactiva el audio para no pedir archivos ausentes. Una vez extraído, «Descargar el libro» ofrece el Markdown; en el sitio publicado ofrece el ZIP.

## Abrir localmente

Abre `index.html` para explorar la presentación o `web/completo.html` para leer todo el texto. El lector carga sus capítulos mediante `web/data/libro.js`, sin `fetch`, para conservar la lectura desde disco.

También puedes servir la carpeta con Python:

```bash
python3 -m http.server 8000
```

Abre <http://localhost:8000>. No hay un servidor de aplicación, registro de usuarios ni instalación de paquetes necesaria para leer la edición generada.

## Editar y compilar

Los archivos de `capitulos/` son la fuente del texto. Para reconstruir los formatos de lectura necesitas Python 3 y `markdown-it-py`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python web/build.py
```

El build actualiza `OBRA-COMPLETA.md`, `indice.md`, `web/data/libro.js`, `web/data/plain/`, `web/completo.html` y la galería de símbolos. También copia los SVG de `simbolos/` y actualiza las versiones de recursos del lector. Edita las fuentes, no estos archivos generados.

Para crear el paquete descargable después de compilar:

```bash
python3 scripts/package.py
```

### Añadir o cambiar un capítulo

```yaml
---
numero: 13
parte: "II · El Camino Práctico"
titulo: "Ritual del Umbral"
slug: "ritual-del-umbral"
resumen: "Una frase para el índice y la cabecera del capítulo."
---
```

El nombre debe ser `<slug>.md` o `NN-<slug>.md`. El número determina el orden. Conserva los slugs existentes para mantener los enlaces compartidos.

Los recuadros del texto admiten `> [!lema]`, `> [!universal]`, `> [!rito]`, `> [!apertura]`, `> [!advertencia]`, `> [!relato]` y `> [!preguntas]`.

### Audio opcional

Los MP3 son narraciones generadas con `edge-tts`. Regenerarlos requiere conexión y envía el texto del capítulo al servicio de síntesis de voz. No hace falta regenerarlos para leer el libro.

En el sitio, los capítulos 00, 02 y 08 muestran su versión revisada en texto y tienen el audio desactivado hasta regenerar esas narraciones. El paquete ZIP no incluye grabaciones.

```bash
python -m pip install edge-tts
python web/generar_audio.py
python web/generar_audio.py --solo 13 --force
```

La generación omite los MP3 existentes salvo que se use `--force`. Después de cambiar un capítulo, su grabación anterior debe identificarse como una edición previa o regenerarse antes de presentarla como narración del texto nuevo.

## Estructura

```text
index.html                 Presentación del producto
README.md                  Esta guía
capitulos/                 Texto fuente con frontmatter
simbolos/                  Nueve símbolos SVG originales
web/
  index.html               Lector por capítulos
  completo.html            Libro entero, generado
  build.py                 Compilador del texto
  generar_audio.py         Generación opcional de voz
  assets/                  Estilos, scripts, imágenes y audio
  data/                    Capítulos y texto plano generados
  simbolos/                Galería y copias de los símbolos
scripts/package.py         Empaquetado de la edición
releases/                  ZIP descargable
OBRA-COMPLETA.md            Obra unificada, generada
indice.md                  Índice, generado
```

## Diseño y método

La presentación sigue el enfoque de libro interactivo de [Taster](https://github.com/josoroma/taster), disponible en este entorno en `/Users/josoroma/sites/taster`: una idea visible, una acción del lector, una consecuencia que se puede examinar y una versión legible del contenido. Los archivos entregados funcionan sin acceder a esa carpeta.

La animación SVG usa una adaptación de `createTransport` de `kit/motion.mjs`, copiada desde Taster con su [licencia MIT](web/assets/vendor/TASTER-LICENSE.txt). No depende del repositorio original en tiempo de ejecución.

El lenguaje visual combina geometría simbólica, espacio, luz y movimiento contenido. La animación acompaña la lectura y respeta la preferencia de movimiento reducido. La distinción editorial es constante: **imaginar, argumentar y comprobar son tareas relacionadas, con criterios diferentes**.

## Verificar la edición

```bash
python3 scripts/check-content.py
```

Comprueba enlaces y capítulos tanto en el sitio como después de extraer el ZIP, ilustraciones, disponibilidad de audio e integridad del archivo.

Para ejecutar las comprobaciones de interacción del DOM (opcional; Node.js moderno):

```bash
npm install --prefix .qa --no-save jsdom@30.1.3
NODE_PATH=.qa/node_modules node scripts/check-interactions.cjs
```

Estas comprobaciones no sustituyen una revisión visual en navegador. La [nota de edición](docs/edicion.md) documenta fuentes, alcance y verificación.

## Publicación en GitHub Pages

La raíz del repositorio es el sitio estático: `index.html` presenta el libro y `web/` conserva el lector y el resto de la edición. Todas las rutas internas son relativas, de modo que funcionan bajo `/el-libro-de-lo-posible/`.

Tras compilar y empaquetar, los archivos pueden publicarse desde la rama y carpeta configuradas en GitHub Pages. La URL del proyecto es <https://josoroma.github.io/el-libro-de-lo-posible/>. Generar el sitio localmente no publica los cambios; el despliegue depende de actualizar el repositorio y de su configuración de Pages.
