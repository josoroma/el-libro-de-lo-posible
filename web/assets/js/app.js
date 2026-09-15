/* ==========================================================================
   El Libro de lo Posible — lógica de la aplicación
   Lector SPA: índice con búsqueda, navegación, progreso, tema, continuidad,
   símbolos y audio por capítulo.
   ========================================================================== */
(function () {
  "use strict";

  const LIBRO = window.LIBRO;
  if (!LIBRO || !Array.isArray(LIBRO.chapters)) return;

  const chapters = LIBRO.chapters;
  const bySlug = {};
  chapters.forEach((c) => (bySlug[c.slug] = c));

  const $ = (sel) => document.querySelector(sel);
  const elIndice = $("#indice");
  const elCapitulo = $("#capitulo");
  const elNavegacion = $("#navegacion");
  const elBarraRelleno = $("#barra-relleno");
  const elVelo = $("#velo");
  const elReproductor = $("#reproductor");

  const STORE = "apertura.progreso";
  const STORE_TEMA = "apertura.tema";

  // ── Estado persistente ─────────────────────────────────────────────────
  function leerEstado() {
    try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch { return {}; }
  }
  function escribirEstado(s) {
    try { localStorage.setItem(STORE, JSON.stringify(s)); } catch {}
  }

  // ── Tema (oscuro por defecto, claro a un clic) ─────────────────────────
  function aplicarTema(t) {
    const oscuro = t === "oscuro";
    document.documentElement.classList.toggle("dark", oscuro);
    $("#tema-icono").textContent = oscuro ? "☾" : "☀";
    $("#tema-texto").textContent = oscuro ? "Tema oscuro" : "Tema claro";
    try { localStorage.setItem(STORE_TEMA, t); } catch {}
  }
  $("#boton-tema").addEventListener("click", () => {
    aplicarTema(document.documentElement.classList.contains("dark") ? "claro" : "oscuro");
  });

  // ── Índice ─────────────────────────────────────────────────────────────
  function construirIndice() {
    const caja = document.createElement("input");
    caja.type = "search";
    caja.id = "buscador";
    caja.className = "indice__buscador";
    caja.placeholder = "Buscar en la obra…";
    caja.setAttribute("aria-label", "Buscar capítulos");
    elIndice.appendChild(caja);

    const contenedor = document.createElement("div");
    contenedor.id = "indice-lista";

    let parteActual = null;
    let fragmento = document.createDocumentFragment();
    chapters.forEach((c) => {
      if (c.parte !== parteActual) {
        parteActual = c.parte;
        const h = document.createElement("div");
        h.className = "indice__parte";
        h.textContent = c.parte;
        fragmento.appendChild(h);
      }
      const a = document.createElement("a");
      a.className = "indice__item";
      a.href = "#" + c.slug;
      a.dataset.slug = c.slug;
      a.dataset.busca = (c.titulo + " " + c.resumen).toLowerCase();
      const num = document.createElement("span");
      num.className = "indice__num";
      num.textContent = c.numero === 0 ? "·" : String(c.numero).padStart(2, "0");
      const t = document.createElement("span");
      t.textContent = c.titulo;
      a.append(num, t);
      fragmento.appendChild(a);
    });

    const extra = document.createElement("div");
    extra.className = "indice__parte";
    extra.textContent = "Materiales";
    const galeria = document.createElement("a");
    galeria.className = "indice__item";
    galeria.href = "simbolos/index.html";
    galeria.innerHTML = '<span class="indice__num">✶</span><span>Símbolos de la Apertura</span>';
    const completo = document.createElement("a");
    completo.className = "indice__item";
    completo.href = "completo.html";
    completo.innerHTML = '<span class="indice__num">▤</span><span>Libro completo (HTML)</span>';
    contenedor.append(fragmento, extra, completo, galeria);
    elIndice.appendChild(contenedor);

    caja.addEventListener("input", () => {
      const q = caja.value.trim().toLowerCase();
      contenedor.querySelectorAll(".indice__item").forEach((a) => {
        const texto = a.dataset.busca || a.textContent.toLowerCase();
        a.style.display = !q || texto.includes(q) ? "" : "none";
      });
      contenedor.querySelectorAll(".indice__parte").forEach((h) => {
        let n = h.nextElementSibling;
        let visible = false;
        while (n && !n.classList.contains("indice__parte")) {
          if (n.classList.contains("indice__item") && n.style.display !== "none") visible = true;
          n = n.nextElementSibling;
        }
        h.style.display = visible ? "" : "none";
      });
    });
  }

  function marcarActivo(slug) {
    elIndice.querySelectorAll(".indice__item").forEach((a) => {
      a.classList.toggle("activo", a.dataset.slug === slug);
    });
    const activo = elIndice.querySelector(".indice__item.activo");
    if (activo) activo.scrollIntoView({ block: "nearest" });
  }

  // ── Render de capítulo ─────────────────────────────────────────────────
  function renderCapitulo(slug) {
    const c = bySlug[slug] || chapters[0];

    elCapitulo.innerHTML = "";
    const parte = document.createElement("p");
    parte.className = "capitulo__parte";
    parte.textContent = c.parte;
    const titulo = document.createElement("h1");
    titulo.className = "capitulo__titulo";
    titulo.textContent = c.titulo;
    const cuerpo = document.createElement("div");
    cuerpo.className = "capitulo__cuerpo";
    cuerpo.innerHTML = c.html;

    elCapitulo.append(parte, titulo);
    if (c.resumen) {
      const resumen = document.createElement("p");
      resumen.className = "capitulo__resumen";
      resumen.textContent = c.resumen;
      elCapitulo.append(resumen);
    }
    elCapitulo.append(cuerpo);

    marcarActivo(c.slug);
    document.title = c.numero === 0 ? LIBRO.titulo : c.titulo + " · " + LIBRO.titulo;
    renderNavegacion(c);
    enlazarInternos();
    prepararAudio(c);

    const estado = leerEstado();
    const pct = estado.posiciones && estado.posiciones[c.slug];
    if (pct != null && !sessionStorage.getItem("apertura.saltar-scroll")) {
      requestAnimationFrame(() => {
        const max = document.documentElement.scrollHeight - window.innerHeight;
        window.scrollTo(0, (pct / 100) * max);
      });
    }
    sessionStorage.removeItem("apertura.saltar-scroll");
  }

  function renderNavegacion(c) {
    elNavegacion.innerHTML = "";
    if (c.prev) {
      elNavegacion.appendChild(crearNav(c.prev, "prev", "← Anterior"));
    } else {
      elNavegacion.appendChild(document.createElement("span"));
    }
    if (c.next) {
      elNavegacion.appendChild(crearNav(c.next, "next", "Siguiente →"));
    }
  }

  function crearNav(slug, dir, rotulo) {
    const c = bySlug[slug];
    const a = document.createElement("a");
    a.className = "nav-enlace nav-enlace--" + (dir === "next" ? "siguiente" : "anterior");
    a.href = "#" + slug;
    const r = document.createElement("span");
    r.className = "nav-enlace__rotulo";
    r.textContent = rotulo;
    const t = document.createElement("span");
    t.className = "nav-enlace__titulo";
    t.textContent = c.titulo;
    a.append(r, t);
    return a;
  }

  function enlazarInternos() {
    elCapitulo.querySelectorAll('a[href^="#"]').forEach((a) => {
      const slug = a.getAttribute("href").slice(1);
      if (bySlug[slug]) {
        a.addEventListener("click", (ev) => {
          ev.preventDefault();
          location.hash = slug;
        });
      }
    });
  }

  // ── Router ─────────────────────────────────────────────────────────────
  function slugActual() {
    const h = location.hash.replace(/^#\/?/, "");
    return bySlug[h] ? h : null;
  }

  function navegar(slug, saltarScroll) {
    if (saltarScroll) sessionStorage.setItem("apertura.saltar-scroll", "1");
    if (location.hash !== "#" + slug) {
      location.hash = slug;
    } else {
      renderCapitulo(slug);
    }
    cerrarMenu();
  }

  function onHash() {
    const s = slugActual();
    if (s) renderCapitulo(s);
  }

  // ── Progreso de lectura ────────────────────────────────────────────────
  let raf = null;
  function actualizarProgreso() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const pct = max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0;
    elBarraRelleno.style.width = pct + "%";

    const s = slugActual();
    if (s) {
      const estado = leerEstado();
      estado.ultimo = s;
      estado.posiciones = estado.posiciones || {};
      estado.posiciones[s] = pct;
      escribirEstado(estado);
    }
    raf = null;
  }
  window.addEventListener("scroll", () => {
    if (!raf) raf = requestAnimationFrame(actualizarProgreso);
  }, { passive: true });

  // ── Menú móvil ─────────────────────────────────────────────────────────
  function abrirMenu() { document.body.classList.add("menu-abierto"); elVelo.hidden = false; }
  function cerrarMenu() { document.body.classList.remove("menu-abierto"); elVelo.hidden = true; }
  $("#boton-menu").addEventListener("click", abrirMenu);
  elVelo.addEventListener("click", cerrarMenu);

  // ── Audio por capítulo ─────────────────────────────────────────────────
  const elAudio = $("#audio");
  const elAudioPlay = $("#audio-play");
  const elAudioBarra = $("#audio-barra");
  const elAudioActual = $("#audio-actual");
  const elAudioTotal = $("#audio-total");
  const elAudioVelocidad = $("#audio-velocidad");
  const elAudioTitulo = $("#audio-titulo");

  /* El reproductor es un overlay fijo: reservamos su altura real para que no
     tape el final del capítulo en ningún breakpoint. */
  function ajustarAltoReproductor() {
    const h = elReproductor.hidden ? 0 : elReproductor.offsetHeight;
    document.documentElement.style.setProperty("--alto-reproductor", h + "px");
  }
  window.addEventListener("resize", ajustarAltoReproductor);

  function prepararAudio(c) {
    elAudioTitulo.textContent = c.titulo;
    elAudio.src = "assets/audio/" + String(c.numero).padStart(2, "0") + "-" + c.slug + ".mp3";
    elAudio.load();
    elAudioPlay.textContent = "▶";
    elAudioBarra.value = 0;
    elAudioActual.textContent = "0:00";
    elAudioTotal.textContent = "0:00";
    elReproductor.hidden = false;
    ajustarAltoReproductor();
  }

  function fmt(t) {
    if (!isFinite(t) || t < 0) return "0:00";
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return m + ":" + String(s).padStart(2, "0");
  }

  elAudio.addEventListener("loadedmetadata", () => {
    elAudioTotal.textContent = fmt(elAudio.duration);
  });
  elAudio.addEventListener("timeupdate", () => {
    if (elAudio.duration) {
      elAudioBarra.value = (elAudio.currentTime / elAudio.duration) * 100;
      elAudioActual.textContent = fmt(elAudio.currentTime);
    }
  });
  elAudio.addEventListener("play", () => { elAudioPlay.textContent = "❚❚"; });
  elAudio.addEventListener("pause", () => { elAudioPlay.textContent = "▶"; });
  elAudio.addEventListener("error", () => {
    /* Si el capítulo no tiene audio, el reproductor desaparece sin romper la
       lectura: todas las funciones siguen disponibles. */
    elReproductor.hidden = true;
    elAudio.pause();
    ajustarAltoReproductor();
  });
  elAudioPlay.addEventListener("click", () => {
    if (elAudio.paused) elAudio.play().catch(() => {}); else elAudio.pause();
  });
  elAudioBarra.addEventListener("input", () => {
    if (elAudio.duration) elAudio.currentTime = (elAudioBarra.value / 100) * elAudio.duration;
  });
  elAudioVelocidad.addEventListener("change", () => {
    elAudio.playbackRate = parseFloat(elAudioVelocidad.value);
  });
  $("#audio-retro").addEventListener("click", () => {
    elAudio.currentTime = Math.max(0, elAudio.currentTime - 15);
  });
  $("#audio-adelante").addEventListener("click", () => {
    elAudio.currentTime = Math.min(elAudio.duration || 0, elAudio.currentTime + 15);
  });

  // ── Inicio ─────────────────────────────────────────────────────────────
  construirIndice();
  aplicarTema((function () {
    try { return localStorage.getItem(STORE_TEMA) || "oscuro"; } catch { return "oscuro"; }
  })());
  ajustarAltoReproductor();
  window.addEventListener("hashchange", onHash);

  const inicial = slugActual();
  if (inicial) {
    renderCapitulo(inicial);
  } else {
    const estado = leerEstado();
    const ultimo = estado.ultimo && bySlug[estado.ultimo] ? estado.ultimo : chapters[0].slug;
    navegar(ultimo);
  }
})();