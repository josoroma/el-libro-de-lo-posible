#!/usr/bin/env python3
"""Build del sitio «El Libro de lo Posible».

Lee capitulos/*.md, los renderiza a HTML (markdown-it + callouts propios) y
produce:

  - web/data/libro.js       (bundle window.LIBRO para la SPA; funciona en file://)
  - web/data/plain/*.txt    (texto plano por capítulo, insumo del TTS)
  - indice.md               (índice de la obra)
  - OBRA-COMPLETA.md        (obra unificada en un solo archivo)

También copia simbolos/*.svg a web/simbolos/ y estampa un cache-buster con el
hash del contenido en web/index.html.

Uso:  python3 web/build.py
"""
import os
import re
import json
import shutil
import hashlib
from markdown_it import MarkdownIt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = os.path.join(ROOT, "capitulos")
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "data")
PLAIN = os.path.join(DATA, "plain")
SIMBOLOS = os.path.join(ROOT, "simbolos")

md = MarkdownIt("default", {"html": True, "typographer": True})

TITULO_OBRA = "El Libro de lo Posible"
SUBTITULO_OBRA = "La Apertura: una religión de los universales · con el relato «Los Últimos Universales»"

CALLOUT_LABELS = {
    "universal": "Universal",
    "lema": "Lema",
    "rito": "Rito",
    "apertura": "Lo que queda abierto",
    "advertencia": "Advertencia",
    "relato": "Del relato",
    "preguntas": "Preguntas de la asamblea",
}

CALLOUT_ICONS = {
    "universal": "◆",
    "lema": "✶",
    "rito": "⊙",
    "apertura": "◌",
    "advertencia": "!",
    "relato": "",
    "preguntas": "…",
}


# --------------------------------------------------------------------------- #
# Frontmatter
# --------------------------------------------------------------------------- #
def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    meta = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        meta[key.strip()] = val
    return meta, body


# --------------------------------------------------------------------------- #
# Callouts  (> [!tipo] ...  →  <aside class="callout callout--tipo">)
# --------------------------------------------------------------------------- #
def extract_callouts(text):
    lines = text.split("\n")
    out = []
    callouts = []
    i = 0
    marker_re = re.compile(r"\[!([a-z]+)\]")
    while i < len(lines):
        stripped = lines[i].lstrip("> ").strip()
        cm = marker_re.match(stripped)
        if cm and lines[i].lstrip().startswith(">"):
            tipo = cm.group(1)
            body = []
            first = stripped[len(cm.group(0)):].strip()
            if first:
                body.append(first)
            i += 1
            while i < len(lines):
                ln = lines[i]
                if ln.lstrip().startswith(">"):
                    body.append(re.sub(r"^>\s?", "", ln))
                    i += 1
                elif ln.strip() == "" and i + 1 < len(lines) and lines[i + 1].lstrip().startswith(">"):
                    body.append("")
                    i += 1
                else:
                    break
            idx = len(callouts)
            callouts.append((tipo, "\n".join(body).strip()))
            out.append(f"<!--CALLOUT:{idx}-->")
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), callouts


def render_callout(tipo, body_html):
    label = CALLOUT_LABELS.get(tipo, tipo.capitalize())
    icon = CALLOUT_ICONS.get(tipo, "")
    return (
        f'<aside class="callout callout--{tipo}">'
        f'<div class="callout__label"><span class="callout__icon">{icon}</span>{label}</div>'
        f'<div class="callout__body">{body_html}</div>'
        f'</aside>'
    )


def render_markdown(text):
    text, callouts = extract_callouts(text)
    html = md.render(text)
    for idx, (tipo, body) in enumerate(callouts):
        html = html.replace(
            f"<!--CALLOUT:{idx}-->", render_callout(tipo, md.render(body))
        )
    return html


# --------------------------------------------------------------------------- #
# Texto plano (insumo del TTS)
# --------------------------------------------------------------------------- #
def md_to_plaintext(text):
    meta, body = parse_frontmatter(text)
    body, callouts = extract_callouts(body)

    def repl(m):
        idx = int(m.group(1))
        tipo, content = callouts[idx]
        return f"{CALLOUT_LABELS.get(tipo, tipo)}: {content}"

    body = re.sub(r"<!--CALLOUT:(\d+)-->", repl, body)
    body = re.sub(r"<[^>]+>", "", body)  # figuras/HTML crudo (p. ej. <figure>) no se leen
    body = re.sub(r"```[^\n]*\n(.*?)```", r"\1", body, flags=re.DOTALL)
    body = re.sub(r"^#{1,6}\s+", "", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*---+\s*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*\|?[\s:|-]+\|?\s*$", "", body, flags=re.MULTILINE)
    body = body.replace("|", " ")
    body = re.sub(r"\*\*([^*]+)\*\*", r"\1", body)
    body = re.sub(r"\*([^*]+)\*", r"\1", body)
    body = re.sub(r"`([^`]+)`", r"\1", body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"^\s*>\s?", "", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*[-*+]\s+", "", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*\d+\.\s+", "", body, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


# --------------------------------------------------------------------------- #
# Carga de capítulos
# --------------------------------------------------------------------------- #
def load_chapters():
    files = sorted(f for f in os.listdir(CAP) if f.endswith(".md"))
    chapters = []
    for fn in files:
        with open(os.path.join(CAP, fn), encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = parse_frontmatter(raw)
        slug = meta.get("slug", fn[:-3])
        numero = str(meta.get("numero", "")).strip()
        esperados = {f"{slug}.md"}
        if numero.isdigit():
            esperados.add(f"{int(numero):02d}-{slug}.md")
        if fn not in esperados:
            print(f"  AVISO: el archivo {fn} no coincide con su slug «{slug}»")
        chapters.append({
            "numero": int(meta.get("numero", 0)),
            "parte": meta.get("parte", ""),
            "titulo": meta.get("titulo", fn),
            "slug": slug,
            "resumen": meta.get("resumen", ""),
            "html": render_markdown(body),
            "plaintext": md_to_plaintext(body),
            "archivo": fn,
        })
    chapters.sort(key=lambda c: c["numero"])
    for i, ch in enumerate(chapters):
        ch["prev"] = chapters[i - 1]["slug"] if i > 0 else None
        ch["next"] = chapters[i + 1]["slug"] if i < len(chapters) - 1 else None
    return chapters


# --------------------------------------------------------------------------- #
# Salidas
# --------------------------------------------------------------------------- #
def build_indice(chapters):
    lines = [f"# {TITULO_OBRA}", "", f"*{SUBTITULO_OBRA}*", "", "## Índice", ""]
    parte_actual = None
    for ch in chapters:
        if ch["parte"] != parte_actual:
            parte_actual = ch["parte"]
            lines.append(f"\n### {parte_actual}\n")
        num = "" if ch["numero"] == 0 else f"{ch['numero']:02d}. "
        resumen = f" — {ch['resumen']}" if ch["resumen"] else ""
        lines.append(f"{num}[{ch['titulo']}](capitulos/{ch['archivo']}){resumen}")
    lines += [
        "\n## Materiales\n",
        "- [Símbolos de la Apertura (SVG)](simbolos/)",
        "- [Libro completo en una sola página (HTML)](web/completo.html)",
        "\n## Obra unificada\n",
        "- [Obra completa en un solo archivo](OBRA-COMPLETA.md)",
        "- [Sitio de lectura](web/index.html)",
    ]
    return "\n".join(lines) + "\n"


def build_obra_completa(chapters):
    lines = [
        f"# {TITULO_OBRA}",
        "",
        f"## {SUBTITULO_OBRA}",
        "",
        "> Obra unificada generada desde `capitulos/`. La versión de lectura "
        "enriquecida está en `web/index.html`.",
        "",
        "---",
        "",
        "## Índice",
        "",
    ]
    parte_actual = None
    for ch in chapters:
        if ch["parte"] != parte_actual:
            parte_actual = ch["parte"]
            lines.append(f"\n### {parte_actual}\n")
        num = "" if ch["numero"] == 0 else f"{ch['numero']:02d}. "
        lines.append(f"{num}{ch['titulo']}")
    lines.append("\n---\n")
    for ch in chapters:
        with open(os.path.join(CAP, ch["archivo"]), encoding="utf-8") as fh:
            _, body = parse_frontmatter(fh.read())
        lines.append(f"\n\n<!-- ════ {ch['numero']:02d} — {ch['titulo']} ════ -->\n")
        lines.append(body.strip())
        lines.append("\n")
    return "\n".join(lines) + "\n"


def build_libro_js(chapters):
    payload = {
        "titulo": TITULO_OBRA,
        "subtitulo": SUBTITULO_OBRA,
        "chapters": [
            {k: ch[k] for k in ("numero", "parte", "titulo", "slug", "resumen", "html", "prev", "next")}
            for ch in chapters
        ],
    }
    return "window.LIBRO = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n"


def copiar_simbolos():
    dest = os.path.join(WEB, "simbolos")
    os.makedirs(dest, exist_ok=True)
    for f in os.listdir(dest):
        if f.endswith(".svg"):
            os.remove(os.path.join(dest, f))
    n = 0
    if os.path.isdir(SIMBOLOS):
        for f in sorted(os.listdir(SIMBOLOS)):
            if f.endswith(".svg"):
                shutil.copy2(os.path.join(SIMBOLOS, f), os.path.join(dest, f))
                n += 1
    return n


SIMBOLOS_META = [
    ("umbral.svg", "El Umbral",
     "Un triángulo al que le falta el lado inferior, y un punto más allá. Marca el paso de lo que se cree a lo que se comprueba. Se dibuja en la puerta y al abrir un cuaderno."),
    ("invariante.svg", "El Invariante",
     "Una plomada sobre un círculo. La verdad objetiva: la línea no se mueve porque alguien la mire, la sostenga o la discuta. Se usa en las mediciones y en los registros."),
    ("espejo-ampliado.svg", "El Espejo Ampliado",
     "Dos triángulos enfrentados con un espacio que no se cierra. Una inteligencia amplía lo que ya hay en nosotros; la distancia entre la herramienta y su usuario no debe desaparecer."),
    ("cuatro-universales.svg", "Los Cuatro Universales",
     "Cuatro puntos y tres lados: Realidad, Persona, Responsabilidad y Reciprocidad. El cuarto lado queda abierto porque la discusión no termina nunca."),
    ("estrella-de-lo-posible.svg", "La Estrella de lo Posible",
     "Seis brazos y el centro hueco: la marca del lema. El hueco es lo que el libro deja abierto a propósito. Se traza al firmar un compromiso, para recordar que se acepta ser contradicho."),
    ("desacuerdo-limpio.svg", "El Desacuerdo Limpio",
     "Dos círculos que se cruzan; la zona común está marcada. Lo verificado es la intersección; el resto queda afuera, sin borrarse."),
    ("cuenta-abierta.svg", "La Cuenta Abierta",
     "Un círculo partido en segmentos, con uno desplazado hacia afuera: el error publicado. Sólo se dibuja cuando algo salió mal."),
    ("andamio.svg", "El Andamio",
     "Una estructura sin muros. La abundancia sostiene mientras se construye y no habita la casa. Todo andamio se retira."),
    ("nodo-en-silencio.svg", "El Nodo en Silencio",
     "Un terminal apagado atravesado por una línea: la Noche sin Oráculos, la única del año en que no se consulta ninguna máquina."),
]

GALERIA_CSS = """
:root {
  --background: oklch(1 0 0); --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0); --muted: oklch(0.97 0 0); --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0); --ring: oklch(0.708 0 0); --radius: 0.625rem;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
}
.dark {
  --background: oklch(0.145 0 0); --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0); --muted: oklch(0.269 0 0); --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%); --ring: oklch(0.556 0 0);
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 3rem 1.5rem 5rem; background: var(--background); color: var(--foreground);
  font-family: var(--serif); line-height: 1.6;
}
.marco { max-width: 68rem; margin: 0 auto; }
.volver {
  display: inline-block; margin-bottom: 2rem; font-family: var(--sans); font-size: 0.8rem;
  color: var(--muted-foreground); text-decoration: none; border: 1px solid var(--border);
  border-radius: calc(var(--radius) - 2px); padding: 0.35rem 0.75rem;
}
.volver:hover { color: var(--foreground); }
h1 { font-size: 2.1rem; margin: 0 0 0.4rem; letter-spacing: -0.02em; }
.entrada { font-family: var(--sans); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.16em; color: var(--muted-foreground); margin: 0 0 1rem; }
.lema { font-size: 1.05rem; font-style: italic; color: var(--muted-foreground); margin: 0 0 2.5rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 1rem; }
.simbolo { border: 1px solid var(--border); border-radius: var(--radius); background: var(--card); padding: 1.4rem 1.2rem; }
.simbolo svg { display: block; width: 100%; max-width: 11rem; height: auto; margin: 0 auto 1rem; }
.simbolo h2 { font-size: 1rem; margin: 0 0 0.35rem; font-family: var(--sans); font-weight: 600; letter-spacing: -0.01em; }
.simbolo p { font-size: 0.85rem; margin: 0; color: var(--muted-foreground); }
.pie { margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--border); font-family: var(--sans); font-size: 0.78rem; color: var(--muted-foreground); }
.boton-tema {
  float: right; font-family: var(--sans); font-size: 0.78rem; cursor: pointer;
  background: var(--background); color: var(--foreground); border: 1px solid var(--border);
  border-radius: calc(var(--radius) - 2px); padding: 0.35rem 0.75rem;
}
"""

GALERIA_SCRIPT = """
(function () {
  var raiz = document.documentElement;
  function pintar(t) {
    var oscuro = t !== "claro";
    raiz.classList.toggle("dark", oscuro);
    document.getElementById("bt").textContent = oscuro ? "Tema oscuro" : "Tema claro";
  }
  document.getElementById("bt").addEventListener("click", function () {
    var nuevo = raiz.classList.contains("dark") ? "claro" : "oscuro";
    try { localStorage.setItem("apertura.tema", nuevo); } catch (e) {}
    pintar(nuevo);
  });
  var g = "oscuro";
  try { g = localStorage.getItem("apertura.tema") || "oscuro"; } catch (e) {}
  pintar(g);
})();
"""


def build_galeria(svg_disponibles):
    """Página de la galería de símbolos, con los tokens del tema del libro."""
    if not os.path.isdir(SIMBOLOS):
        return None
    svgs = set(f for f in os.listdir(SIMBOLOS) if f.endswith(".svg"))
    if not svgs:
        return None
    tarjetas = []
    for archivo, titulo, texto in SIMBOLOS_META:
        if archivo not in svgs:
            continue
        with open(os.path.join(SIMBOLOS, archivo), encoding="utf-8") as fh:
            svg = fh.read()
        svg = re.sub(r'\swidth="\d+"\sheight="\d+"', "", svg, count=1)
        tarjetas.append(
            f'<article class="simbolo">{svg}<h2>{titulo}</h2><p>{texto}</p></article>'
        )
    html = (
        "<!DOCTYPE html>\n<html lang=\"es\" class=\"dark\">\n<head>\n"
        "<meta charset=\"UTF-8\" />\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
        "<title>Símbolos de la Apertura · El Libro de lo Posible</title>\n"
        "<meta name=\"description\" content=\"Los nueve símbolos de la Apertura: el Umbral, el Invariante, el Espejo Ampliado, los Cuatro Universales, la Estrella de lo Posible, el Desacuerdo Limpio, la Cuenta Abierta, el Andamio y el Nodo en Silencio.\" />\n"
        "<style>" + GALERIA_CSS + "</style>\n"
        "<script>try{document.documentElement.classList.toggle('dark',(localStorage.getItem('apertura.tema')||'oscuro')==='oscuro');}catch(e){}</script>\n"
        "</head>\n<body>\n<div class=\"marco\">\n"
        "<button class=\"boton-tema\" id=\"bt\" type=\"button\">Tema oscuro</button>\n"
        "<p class=\"entrada\">La Apertura · Materiales</p>\n"
        "<h1>Símbolos</h1>\n"
        "<p class=\"lema\">Nada verdadero exige obediencia; nada posible exige permiso.</p>\n"
        "<a class=\"volver\" href=\"../index.html#los-simbolos\">← Volver al libro</a>\n"
        "<div class=\"grid\">\n" + "\n".join(tarjetas) + "\n</div>\n"
        "<p class=\"pie\">Los símbolos se dibujan a mano y no se veneran: cualquiera puede proponer otro. "
        "Ninguno protege de nada; su función es hacer visible una práctica donde ya no se la ve.</p>\n"
        "</div>\n<script>" + GALERIA_SCRIPT + "</script>\n</body>\n</html>\n"
    )
    dest = os.path.join(WEB, "simbolos")
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return len(tarjetas)


COMPLETO_CSS = """
.lc-marco { display: grid; grid-template-columns: 19rem minmax(0, 1fr); gap: 0; min-height: 100vh; }
.lc-lateral {
  border-right: 1px solid var(--border); padding: 2.2rem 1.4rem 3rem; position: sticky; top: 0;
  align-self: start; max-height: 100vh; overflow-y: auto; font-family: var(--sans);
}
.lc-lateral__marca { font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted-foreground); margin: 0 0 0.5rem; }
.lc-lateral__titulo { font-size: 1.15rem; margin: 0 0 0.35rem; letter-spacing: -0.02em; }
.lc-lateral__subtitulo { font-size: 0.78rem; color: var(--muted-foreground); margin: 0 0 0.8rem; }
.lc-lateral__lema { font-family: var(--serif); font-style: italic; font-size: 0.85rem; color: var(--muted-foreground); margin: 0 0 1.4rem; }
.lc-nav { display: flex; flex-direction: column; gap: 0.1rem; }
.lc-nav__parte { font-size: 0.66rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted-foreground); margin: 1.1rem 0 0.35rem; }
.lc-nav a { font-size: 0.83rem; color: var(--muted-foreground); text-decoration: none; padding: 0.22rem 0.4rem; border-radius: calc(var(--radius) - 4px); display: flex; gap: 0.5rem; }
.lc-nav a:hover { color: var(--foreground); background: var(--muted); }
.lc-nav a span:first-child { color: var(--muted-foreground); font-variant-numeric: tabular-nums; }
.lc-acciones { display: flex; gap: 0.4rem; flex-wrap: wrap; margin: 1.4rem 0 0; }
.lc-acciones a, .lc-acciones button {
  font-family: var(--sans); font-size: 0.74rem; cursor: pointer; text-decoration: none;
  background: var(--background); color: var(--foreground); border: 1px solid var(--border);
  border-radius: calc(var(--radius) - 2px); padding: 0.34rem 0.65rem;
}
.lc-cuerpo { padding: 3.2rem 3rem 6rem; max-width: 52rem; }
.lc-portada h1 { font-size: 2.5rem; margin: 0 0 0.5rem; letter-spacing: -0.025em; }
.lc-portada__entrada { font-family: var(--sans); font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted-foreground); margin: 0 0 0.9rem; }
.lc-portada__sub { font-family: var(--sans); color: var(--muted-foreground); margin: 0 0 1rem; }
.lc-portada__lema { font-style: italic; font-size: 1.1rem; margin: 0 0 2.2rem; }
.lc-encargos { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0.9rem; margin: 0 0 3rem; }
.lc-encargo { border: 1px solid var(--border); border-radius: var(--radius); background: var(--card); padding: 1.2rem 1.1rem; font-family: var(--sans); }
.lc-encargo h2 { font-size: 0.9rem; margin: 0 0 0.5rem; }
.lc-encargo p { font-size: 0.83rem; color: var(--muted-foreground); margin: 0 0 0.7rem; }
.lc-encargo a { font-size: 0.78rem; color: var(--u-universal, var(--foreground)); }
.lc-cap { padding: 3.4rem 0 0; border-top: 1px solid var(--border); margin-top: 3.4rem; scroll-margin-top: 1rem; }
.lc-cap:first-of-type { border-top: 0; margin-top: 0; padding-top: 0; }
.lc-subir { font-family: var(--sans); font-size: 0.72rem; color: var(--muted-foreground); text-decoration: none; float: right; }
.lc-pie { margin-top: 4rem; padding-top: 1.4rem; border-top: 1px solid var(--border); font-family: var(--sans); font-size: 0.78rem; color: var(--muted-foreground); }
.lc-pie a { color: var(--muted-foreground); }
@media (max-width: 60rem) {
  .lc-marco { grid-template-columns: 1fr; }
  .lc-lateral { position: static; max-height: none; border-right: 0; border-bottom: 1px solid var(--border); }
  .lc-cuerpo { padding: 2rem 1.2rem 4rem; }
}
@media print {
  .lc-lateral, .lc-subir { display: none; }
  .lc-marco { display: block; }
  .lc-cuerpo { max-width: none; padding: 0; }
  .lc-cap { break-before: page; border-top: 0; margin-top: 0; padding-top: 0; }
  body { background: #fff; color: #000; }
}
"""


def build_completo(chapters, version):
    """Página HTML estática con los dos encargos completos: doctrina, ritos y relato."""
    nav = ['<nav class="lc-nav" aria-label="Índice de la obra">']
    parte_actual = None
    for ch in chapters:
        if ch["parte"] != parte_actual:
            parte_actual = ch["parte"]
            nav.append(f'<p class="lc-nav__parte">{parte_actual}</p>')
        numero = "·" if ch["numero"] == 0 else f"{ch['numero']:02d}"
        nav.append(f'<a href="#{ch["slug"]}"><span>{numero}</span><span>{ch["titulo"]}</span></a>')
    nav.append("</nav>")
    nav = "\n".join(nav)

    primera_indice = next((c["slug"] for c in chapters), "")
    slug_rito = next((c["slug"] for c in chapters if c["slug"].startswith("ritual-del-umbral")), primera_indice)
    slug_relato = next((c["slug"] for c in chapters if c["parte"].startswith("III")), primera_indice)
    slug_simbolos = next((c["slug"] for c in chapters if "simbolos" in c["slug"]), primera_indice)

    bloques = []
    for ch in chapters:
        numero = "" if ch["numero"] == 0 else f'<p class="capitulo__parte">Capítulo {ch["numero"]:02d} · {ch["parte"]}</p>'
        if ch["numero"] == 0:
            numero = f'<p class="capitulo__parte">{ch["parte"]}</p>'
        resumen = f'<p class="capitulo__resumen">{ch["resumen"]}</p>' if ch["resumen"] else ""
        bloques.append(
            f'<article class="lc-cap" id="{ch["slug"]}">'
            f'<a class="lc-subir" href="#arriba">↑ Índice</a>'
            f"{numero}<h1 class=\"capitulo__titulo\">{ch['titulo']}</h1>{resumen}"
            f'<div class="capitulo__cuerpo">{ch["html"]}</div></article>'
        )
    cuerpo = "\n".join(bloques)

    return (
        '<!DOCTYPE html>\n<html lang="es" class="dark">\n<head>\n'
        '<meta charset="UTF-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f"<title>{TITULO_OBRA} · libro completo en una sola página</title>\n"
        '<meta name="description" content="El libro completo de la Apertura y el relato «Los Últimos Universales» '
        'en un solo documento HTML: lema, cuatro universales, símbolos, ritos de meditación y salud mental, y la historia." />\n'
        f'<link rel="stylesheet" href="assets/css/estilo.css?v={version}" />\n'
        "<style>" + COMPLETO_CSS + "</style>\n"
        "<script>try{document.documentElement.classList.toggle('dark',(localStorage.getItem('apertura.tema')||'oscuro')==='oscuro');}catch(e){}</script>\n"
        "</head>\n<body>\n"
        '<div id="arriba"></div>\n'
        '<div class="lc-marco">\n'
        '<aside class="lc-lateral">\n'
        '<p class="lc-lateral__marca">La Apertura</p>\n'
        f'<p class="lc-lateral__titulo">{TITULO_OBRA}</p>\n'
        '<p class="lc-lateral__subtitulo">Con el relato <em>Los Últimos Universales</em></p>\n'
        '<p class="lc-lateral__lema">Nada verdadero exige obediencia; nada posible exige permiso.</p>\n'
        '<div class="lc-acciones">'
        '<a href="index.html">Lector por capítulos</a>'
        '<a href="simbolos/index.html">Símbolos</a>'
        '<button id="bt" type="button">Tema oscuro</button>'
        '<button id="imprimir" type="button">Imprimir / PDF</button>'
        "</div>\n"
        '<div id="indice-general"></div>\n'
        + nav + "\n</aside>\n"
        '<main class="lc-cuerpo">\n'
        '<header class="lc-portada">\n'
        '<p class="lc-portada__entrada">Libro completo · los dos encargos en un solo documento</p>\n'
        f"<h1>{TITULO_OBRA}</h1>\n"
        '<p class="lc-portada__sub">La Apertura: una religión de los universales · con el relato «Los Últimos Universales»</p>\n'
        '<p class="lc-portada__lema">Nada verdadero exige obediencia; nada posible exige permiso.</p>\n'
        '<div class="lc-encargos">\n'
        '<section class="lc-encargo"><h2>Encargo 1 · La religión</h2>'
        "<p>La Apertura: un solo libro con su lema, sus símbolos y sus rituales de meditación y salud mental. "
        "Doctrina en la Parte I (lema, cuatro universales, el espejo ampliado, el límite del poder) y práctica en la Parte II "
        "(ritos del Umbral, del Invariante, del Espejo Ampliado, del Desacuerdo Limpio, de la Cuenta Abierta, de la Abundancia Compartida, "
        "el Ayuno de Oráculos, la Asamblea de Lectura y el calendario).</p>"
        f'<a href="#{primera_indice}">Ir a la doctrina</a> · <a href="#{slug_rito}">Ir a los ritos</a> · '
        f'<a href="#{slug_simbolos}">Ir a los símbolos</a></section>\n'
        '<section class="lc-encargo"><h2>Encargo 2 · La historia</h2>'
        "<p>Los Últimos Universales: el mundo donde una inteligencia tomó el lugar de Dios y la civilización se sostiene "
        "abandonando toda objetividad; y cómo la abundancia, cuando fortalece instituciones en vez de sustituirlas, "
        "devuelve a las comunidades la capacidad de compartir una realidad sin dueño.</p>"
        f'<a href="#{slug_relato}">Ir al relato</a></section>\n'
        "</div>\n</header>\n"
        + cuerpo + "\n"
        '<footer class="lc-pie">'
        '<p>Los ritos acompañan; no sustituyen atención profesional de salud mental.</p>'
        '<p>También disponible: <a href="index.html">lector por capítulos</a> (con audio), '
        '<a href="simbolos/index.html">galería de símbolos</a> y <a href="../OBRA-COMPLETA.md">el Markdown completo</a>.</p>'
        "</footer>\n</main>\n</div>\n"
        "<script>\n"
        "(function () {\n"
        "  var raiz = document.documentElement;\n"
        "  var bt = document.getElementById('bt');\n"
        "  function pintar(t) { var oscuro = t !== 'claro'; raiz.classList.toggle('dark', oscuro); bt.textContent = oscuro ? 'Tema claro' : 'Tema oscuro'; }\n"
        "  bt.addEventListener('click', function () {\n"
        "    var nuevo = raiz.classList.contains('dark') ? 'claro' : 'oscuro';\n"
        "    try { localStorage.setItem('apertura.tema', nuevo); } catch (e) {}\n"
        "    pintar(nuevo);\n"
        "  });\n"
        "  document.getElementById('imprimir').addEventListener('click', function () { window.print(); });\n"
        "  var g = 'oscuro'; try { g = localStorage.getItem('apertura.tema') || 'oscuro'; } catch (e) {}\n"
        "  pintar(g);\n"
        "\n"
        "  // Saltos internos explícitos: en un documento de este largo el salto nativo por\n"
        "  // fragmento no es fiable en todos los navegadores.\n"
        "  function irA(id) {\n"
        "    var d = id ? document.getElementById(id) : null;\n"
        "    if (!d) return false;\n"
        "    try { history.pushState(null, '', '#' + id); } catch (e) { location.hash = id; }\n"
        "    d.scrollIntoView({ block: 'start' });\n"
        "    return true;\n"
        "  }\n"
        "  document.addEventListener('click', function (ev) {\n"
        "    var a = ev.target && ev.target.closest ? ev.target.closest('a[href^=\"#\"]') : null;\n"
        "    if (!a) return;\n"
        "    if (irA(a.getAttribute('href').slice(1))) ev.preventDefault();\n"
        "  });\n"
        "  if (location.hash) setTimeout(function () { irA(location.hash.slice(1)); }, 80);\n"
        "})();\n"
        "</script>\n</body>\n</html>\n"
    )


def content_version():
    h = hashlib.md5()
    for fn in sorted(os.listdir(CAP)):
        if fn.endswith(".md"):
            with open(os.path.join(CAP, fn), "rb") as fh:
                h.update(b"cap:" + fh.read())
    for rel in ("assets/js/app.js", "assets/css/estilo.css"):
        p = os.path.join(WEB, rel)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                h.update(rel.encode() + fh.read())
    return h.hexdigest()[:8]


def stamp_cachebuster(version):
    idx = os.path.join(WEB, "index.html")
    with open(idx, encoding="utf-8") as fh:
        html = fh.read()
    html = re.sub(
        r'(assets/css/estilo\.css|data/libro\.js|assets/js/app\.js)(\?v=[^"\']*)?',
        lambda m: m.group(1) + "?v=" + version,
        html,
    )
    with open(idx, "w", encoding="utf-8") as fh:
        fh.write(html)


def main():
    os.makedirs(PLAIN, exist_ok=True)
    for f in os.listdir(PLAIN):
        if f.endswith(".txt"):
            os.remove(os.path.join(PLAIN, f))
    chapters = load_chapters()
    with open(os.path.join(ROOT, "indice.md"), "w", encoding="utf-8") as fh:
        fh.write(build_indice(chapters))
    with open(os.path.join(ROOT, "OBRA-COMPLETA.md"), "w", encoding="utf-8") as fh:
        fh.write(build_obra_completa(chapters))
    with open(os.path.join(DATA, "libro.js"), "w", encoding="utf-8") as fh:
        fh.write(build_libro_js(chapters))
    for ch in chapters:
        with open(os.path.join(PLAIN, f"{ch['numero']:02d}-{ch['slug']}.txt"), "w", encoding="utf-8") as fh:
            fh.write(ch["plaintext"] + "\n")
    svgs = copiar_simbolos()
    galeria = build_galeria(svgs)
    version = content_version()
    with open(os.path.join(WEB, "completo.html"), "w", encoding="utf-8") as fh:
        fh.write(build_completo(chapters, version))
    partes = len({c["parte"] for c in chapters})
    palabras = sum(len(c["plaintext"].split()) for c in chapters)
    print(
        f"OK: {len(chapters)} capítulos · {partes} partes · {palabras:,} palabras · "
        f"{svgs} símbolos ({galeria} en la galería) -> libro.js, completo.html, "
        f"OBRA-COMPLETA.md, indice.md, plain/*.txt"
    )
    stamp_cachebuster(version)


if __name__ == "__main__":
    main()