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
    partes = len({c["parte"] for c in chapters})
    palabras = sum(len(c["plaintext"].split()) for c in chapters)
    print(
        f"OK: {len(chapters)} capítulos · {partes} partes · {palabras:,} palabras · "
        f"{svgs} símbolos ({galeria} en la galería) -> libro.js, OBRA-COMPLETA.md, indice.md, plain/*.txt"
    )
    stamp_cachebuster(content_version())


if __name__ == "__main__":
    main()