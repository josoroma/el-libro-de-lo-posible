# El Libro de lo Posible

La Apertura: una religión de los universales, sin misticismo y con la puerta abierta.
Incluye, como parte del mismo libro, el relato **Los Últimos Universales**.

**▶ Leer en línea: <https://josoroma.github.io/el-libro-de-lo-posible/>**
([libro completo en una sola página](https://josoroma.github.io/el-libro-de-lo-posible/web/completo.html) ·
[galería de símbolos](https://josoroma.github.io/el-libro-de-lo-posible/web/simbolos/))

- **36 capítulos** en cuatro partes: *Apertura* (portada), *I · El Libro de lo Posible* (doctrina),
  *II · El Camino Práctico* (ritos, asamblea, calendario) y *III · Los Últimos Universales* (relato).
- **Lema:** «Nada verdadero exige obediencia; nada posible exige permiso.»
- **Cuatro universales:** Realidad, Persona, Responsabilidad, Reciprocidad.
- **Nueve símbolos** dibujados en SVG, con su significado y su uso.

## Estructura

```
capitulos/           # fuente: un archivo Markdown por capítulo, con frontmatter YAML
simbolos/            # los nueve símbolos en SVG (fuente)
web/                 # lector: sitio estático listo para GitHub Pages
  build.py           # compila los capítulos -> libro.js, OBRA-COMPLETA.md, indice.md, plain/
  generar_audio.py   # audio por capítulo (edge-tts, voz es-MX-DaliaNeural)
  index.html         # lector de página única, tema oscuro por defecto
  completo.html      # generado: el libro entero (los dos encargos) en una sola página HTML
  assets/css/estilo.css
  assets/js/app.js
  data/              # generado: libro.js + plain/*.txt (insumo del audio)
  simbolos/          # generado: copia de los SVG + galería
  assets/audio/      # generado: un mp3 por capítulo
index.html           # redirección a web/index.html (raíz del sitio)
OBRA-COMPLETA.md     # generado: el libro completo en un solo Markdown
indice.md            # generado: índice con resúmenes
```

## Compilar

```bash
python3 web/build.py          # capítulos -> lector + obra completa + texto plano
python3 web/generar_audio.py  # audio de los capítulos que falten
python3 web/generar_audio.py --desde 13 --hasta 21 --force
```

`build.py` no edita nada a mano: `OBRA-COMPLETA.md`, `indice.md`, `web/data/libro.js`,
`web/data/plain/` y `web/simbolos/index.html` se regeneran siempre. Para cambiar el texto,
se editan los archivos de `capitulos/`, que es la única fuente.

## Frontmatter de un capítulo

```yaml
---
numero: 13
parte: "II · El Camino Práctico"
titulo: "Ritual del Umbral"
slug: "ritual-del-umbral"
resumen: "Una frase que aparece en el índice y en la cabecera del capítulo."
---
```

El nombre del archivo debe ser `<slug>.md` (o `NN-<slug>.md` con el mismo número del frontmatter).
Los capítulos se ordenan por `numero`.

## Formatos del sitio

| Ruta | Formato | Contenido |
|---|---|---|
| `web/index.html` | SPA (JavaScript) | lector por capítulos, con índice, buscador y audio |
| `web/completo.html` | **HTML estático** | el libro completo en una sola página (los dos encargos), con índice por anclas e «Imprimir / PDF» |
| `web/simbolos/index.html` | HTML estático | galería de los nueve símbolos |
| `OBRA-COMPLETA.md` | Markdown | la obra unificada, sin dependencias |

`completo.html` no necesita JavaScript para mostrar el texto: lo único que usa script es el
conmutador de tema y el botón de impresión. Por eso sirve también sin conexión y para imprimir o
exportar a PDF desde el navegador.

## Lector

- Tema **shadcn «luma»**, oscuro por defecto y claro a un clic; la preferencia se guarda en el navegador
  y se comparte entre el lector, el libro completo y la galería.
- Índice lateral agrupado por partes, buscador de capítulos, enrutado por hash (enlaces compartibles),
  barra de progreso de lectura, navegación anterior/siguiente y reproductor de audio por capítulo.
- Funciona abierto directamente desde el disco (`file://`) porque el contenido se carga por
  `<script src="data/libro.js">` y no por `fetch`.

## Callouts

Los capítulos usan blockquotes marcados, que `build.py` convierte en recuadros:

| Marca | Rótulo |
|---|---|
| `> [!lema]` | Lema |
| `> [!universal]` | Universal |
| `> [!rito]` | Rito |
| `> [!apertura]` | Lo que queda abierto |
| `> [!advertencia]` | Advertencia |
| `> [!relato]` | Del relato |
| `> [!preguntas]` | Preguntas de la asamblea |

## Publicación

**Sitio:** <https://josoroma.github.io/el-libro-de-lo-posible/>

| Sección del sitio | URL |
|---|---|
| Lector por capítulos (con audio) | <https://josoroma.github.io/el-libro-de-lo-posible/> |
| Libro completo en una sola página | <https://josoroma.github.io/el-libro-de-lo-posible/web/completo.html> |
| Galería de los nueve símbolos | <https://josoroma.github.io/el-libro-de-lo-posible/web/simbolos/> |

El sitio se publica desde la raíz del repositorio: `index.html` redirige a `web/index.html`,
y todos los recursos usan rutas relativas. No hay dependencias ni proceso de compilación en el
servidor; el HTML generado se abre tal cual.

Para publicar cambios: `python3 web/build.py`, commit y push a `main`. GitHub Pages reconstruye
el sitio en unos 60–90 segundos. Si el sitio se crea desde cero:

```bash
printf '%s' '{"source":{"branch":"main","path":"/"}}' | gh api --method POST repos/josoroma/el-libro-de-lo-posible/pages --input -
```

Para el `About` del repositorio (ya activado), la URL del sitio se cambia con:

```bash
gh api --method PATCH repos/josoroma/el-libro-de-lo-posible --field homepage='https://josoroma.github.io/el-libro-de-lo-posible/' --jq .homepage
```