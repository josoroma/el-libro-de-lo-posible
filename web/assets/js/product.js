/* El Libro de lo Posible — local, dependency-free interaction.
 * Animation transport adapted from the user's Taster kit (MIT).
 * Every figure is a metaphor, never a quantitative physical model. */
(function () {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const steps = [
    { kind: 'UNA POSIBILIDAD / NO UNA PREDICCIÓN', question: '¿Y si una ciudad pudiera acabar con el hambre?', description: 'Imagina energía abundante, máquinas que producen alimentos y tiempo para cuidarnos. La ficción permite explorar esa posibilidad antes de saber si podemos realizarla.', rule: 'Abre un escenario. Todavía no demuestra que sea posible ni que vaya a ocurrir.', chapter: 'El hambre en la abundancia', slug: 'el-hambre-en-la-abundancia' },
    { kind: 'UN JUICIO ÉTICO / NO UNA MEDICIÓN', question: '¿Quién decide cómo se reparte esa abundancia?', description: 'Una ciudad puede producir mucho y tratar mal a sus habitantes. Pregunta quién decide, quién queda fuera y quién responde por el daño. Tener más recursos no resuelve por sí solo esos desacuerdos.', rule: 'Examina valores y consecuencias. Una decisión justa necesita razones que otras personas puedan discutir.', chapter: 'Los cuatro universales', slug: 'los-cuatro-universales' },
    { kind: 'UNA AFIRMACIÓN / EVIDENCIA NECESARIA', question: '¿Cómo sabríamos si de verdad disminuye el hambre?', description: 'Habría que definir qué medimos, registrar el acceso real a alimentos, comparar periodos y revisar quién falta en los datos. También buscar resultados que contradigan la promesa.', rule: 'Propone una comprobación. El ejemplo no aporta datos reales ni demuestra que una política funcione.', chapter: 'La asamblea de verificación', slug: 'la-asamblea-de-verificacion' },
    { kind: 'UNA PREGUNTA METAFÍSICA / SIN RESPUESTA CERRADA', question: '¿Tiene el universo un propósito que nos incluya?', description: 'Puedes imaginar respuestas y examinar sus argumentos. El libro no dispone de una demostración que resuelva esta pregunta. La falta de explicación permite seguir investigando; no convierte una conjetura en un hecho.', rule: 'Conserva la incógnita. Una explicación sobrenatural tampoco queda demostrada porque falte otra explicación.', chapter: 'Lo que este libro no decide', slug: 'lo-que-el-libro-no-decide' }
  ];
  const tabs = [...document.querySelectorAll('[data-step]')];
  function selectStep(index, focus = false) {
    const step = steps[index];
    tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(index === i)); tab.tabIndex = index === i ? 0 : -1; });
    $('#lab-panel').setAttribute('aria-labelledby', tabs[index].id);
    $('#lab-kind').textContent = step.kind;
    $('#lab-question').textContent = step.question;
    $('#lab-description').textContent = step.description;
    $('#lab-rule').textContent = step.rule;
    $('#lab-chapter').textContent = 'Llévalo al libro: ' + step.chapter + ' ↗';
    $('#lab-chapter').href = 'web/index.html#' + step.slug;
    $('#figure-number').textContent = ['I', 'II', 'III', 'IV'][index] + ' / IV';
    document.querySelectorAll('[data-orbit]').forEach((ring, i) => { ring.setAttribute('stroke', i === index ? '#d8e5b7' : '#61765f'); ring.setAttribute('stroke-width', i === index ? '2.6' : '1'); });
    if (focus) tabs[index].focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectStep(index));
    tab.addEventListener('keydown', (event) => {
      let next;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectStep(next, true); }
    });
  });
  document.querySelectorAll('[data-answer]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-answer]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    $('#check-feedback').textContent = button.dataset.answer === 'open'
      ? 'Exacto. Podemos explorar hipótesis, incluida la metafísica, y mantener la pregunta abierta. Afirmar una causa requiere razones y, cuando es comprobable, evidencia.'
      : 'La falta de una explicación no demuestra otra. Puedes proponer esa causa como hipótesis, pero todavía tendrías que justificarla. Prueba la otra respuesta.';
  }));
  const symbols = [
    ['El Umbral', 'Antes de cruzar: nombra lo que sabes, lo que supones y lo que todavía no sabes.', 'umbral'],
    ['El Invariante', 'Una plomada recuerda que una afirmación sobre la realidad debe resistir la comprobación, no solo resultar convincente.', 'invariante'],
    ['El Espejo Ampliado', 'Una inteligencia puede ampliar nuestras capacidades y nuestros errores. Consulta, verifica y conserva la responsabilidad de decidir.', 'espejo-ampliado'],
    ['Los Cuatro Universales', 'Realidad, Persona, Responsabilidad y Reciprocidad: cuatro compromisos filosóficos para discutir cómo convivir.', 'cuatro-universales'],
    ['La Estrella de lo Posible', 'El centro queda abierto. Firmar un compromiso incluye aceptar preguntas, objeciones y correcciones.', 'estrella-de-lo-posible'],
    ['El Desacuerdo Limpio', 'Conserva lo que puedes comprobar en común. Documenta lo que sigue en disputa sin borrar a la otra persona.', 'desacuerdo-limpio'],
    ['La Cuenta Abierta', 'El segmento desplazado recuerda el error que se hace público: qué decidiste, a quién afectó y qué queda por reparar.', 'cuenta-abierta'],
    ['El Andamio', 'La abundancia es un soporte. Pregunta si la herramienta libera tiempo para los vínculos y las instituciones que quieres cuidar.', 'andamio'],
    ['El Nodo en Silencio', 'Interrumpe la consulta automática. Descubre qué preguntas aparecen cuando ninguna máquina responde por ti.', 'nodo-en-silencio']
  ];
  document.querySelectorAll('[data-symbol]').forEach((button) => button.addEventListener('click', () => {
    const symbol = symbols[Number(button.dataset.symbol)];
    document.querySelectorAll('[data-symbol]').forEach((item) => { const selected = item === button; item.classList.toggle('selected', selected); item.setAttribute('aria-pressed', String(selected)); });
    $('#symbol-title').textContent = symbol[0];
    $('#symbol-description').textContent = symbol[1];
    $('#symbol-download').href = 'simbolos/' + symbol[2] + '.svg';
  }));
  // No unsolicited motion. Playback is explicit and pauses on tab/section exit.
  const transport = window.Taster.createTransport({ duration: 40, loop: true });
  const motion = $('#motion-toggle');
  const seek = $('#motion-seek');
  const orbit = $('#instrument-orbit');
  let frame = null;
  let previousTime = null;
  function renderMotion() {
    const state = transport.getState();
    orbit.setAttribute('transform', 'rotate(' + (state.progress * 360).toFixed(3) + ' 240 190)');
    seek.value = state.progress * 100;
    motion.setAttribute('aria-pressed', String(state.playing));
    motion.textContent = state.playing ? 'Ⅱ Pausar símbolo' : '▷ Animar símbolo';
  }
  function tick(now) {
    frame = null;
    if (previousTime !== null) transport.update(Math.min((now - previousTime) / 1000, 0.1));
    previousTime = now;
    renderMotion();
    if (transport.getState().playing) frame = requestAnimationFrame(tick);
  }
  function pause() {
    transport.pause();
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null; previousTime = null; renderMotion();
  }
  motion.addEventListener('click', () => {
    if (transport.getState().playing) pause();
    else { transport.play(); previousTime = null; renderMotion(); frame = requestAnimationFrame(tick); }
  });
  seek.addEventListener('input', () => { const requested = Number(seek.value); pause(); transport.seek(requested / 100 * 40); renderMotion(); });
  // Store the slider's requested value before pause redraws it.
  seek.addEventListener('pointerdown', () => pause());
  $('#motion-reset').addEventListener('click', () => { pause(); transport.seek(0); renderMotion(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  reducedMotion.addEventListener('change', () => pause());
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => { if (!entries[0].isIntersecting) pause(); }, { threshold: 0.05 });
    observer.observe($('#instrument'));
  }
  selectStep(0);
  renderMotion();
})();
