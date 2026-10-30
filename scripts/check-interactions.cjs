const { JSDOM } = require('jsdom');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const root = process.cwd();
let checks = 0;
function verify(value, message) { assert.ok(value, message); checks++; }
function setup(file, hash='') {
 const dom = new JSDOM(fs.readFileSync(file, 'utf8'), { url: 'http://localhost/' + file + hash, runScripts: 'outside-only', pretendToBeVisual: true });
 const w = dom.window;
 const mediaListeners = [];
 w.matchMedia = () => ({ matches: true, addEventListener: (_, listener) => mediaListeners.push(listener) });
 w.HTMLElement.prototype.scrollIntoView = () => {};
 w.scrollTo = () => {};
 w.HTMLMediaElement.prototype.pause = function() {};
 w.HTMLMediaElement.prototype.load = function() {};
 w.HTMLMediaElement.prototype.play = function() { return Promise.resolve(); };
 const load = (name) => w.eval(fs.readFileSync(name, 'utf8'));
 return {dom,w,load,mediaListeners};
}
const {dom,w,load,mediaListeners} = setup('index.html');
load('web/assets/vendor/taster-transport.js');
load('web/assets/js/product.js');
const $ = (s) => w.document.querySelector(s);
const click = (s) => $(s).click();
verify($('#motion-toggle').getAttribute('aria-pressed') === 'false', 'No automatic motion, including reduced-motion preference');
for (let i=0;i<4;i++) {
 click('[data-step="'+i+'"]');
 verify(w.document.querySelectorAll('[role=tab][aria-selected=true]').length===1,'Exactly one selected tab');
 verify($('#lab-panel').getAttribute('aria-labelledby') === $('[data-step="'+i+'"]').id,'Panel points to active tab');
 verify($('#figure-number').textContent.startsWith(['I /','II /','III /','IV /'][i]),'Figure reflects semantic step');
}
$('#tab-abrir').dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
verify(w.document.activeElement.id==='tab-imaginar','Arrow key wraps to first tab');
$('#tab-imaginar').dispatchEvent(new w.KeyboardEvent('keydown',{key:'End',bubbles:true}));
verify(w.document.activeElement.id==='tab-abrir','End reaches final tab');
verify($('#lab-description').textContent.includes('no convierte una conjetura'),'Metaphysics remains explicitly unproven');
click('[data-answer="cause"]');
verify($('#check-feedback').textContent.includes('no demuestra otra'),'Wrong answer gives reason');
click('[data-answer="open"]');
verify($('#check-feedback').textContent.startsWith('Exacto'),'Retry succeeds');
for(let i=0;i<9;i++) {
 click('[data-symbol="'+i+'"]');
 verify(w.document.querySelectorAll('.symbol-button[aria-pressed=true]').length===1,'One selected symbol');
 verify(fs.existsSync(root+'/'+$('#symbol-download').getAttribute('href')),'Download targets actual SVG');
}
$('#motion-seek').value='50'; $('#motion-seek').dispatchEvent(new w.Event('input',{bubbles:true}));
verify($('#instrument-orbit').getAttribute('transform')==='rotate(180.000 240 190)','Seek reaches exact requested rotation');
verify($('#motion-seek').value==='50','Seek is preserved through pause redraw');
click('#motion-toggle'); verify($('#motion-toggle').getAttribute('aria-pressed')==='true','Explicit playback starts');
click('#motion-toggle'); verify($('#motion-toggle').getAttribute('aria-pressed')==='false','Pause works');
click('#motion-reset'); verify($('#motion-seek').value==='0','Reset returns exact start');
click('#motion-toggle'); mediaListeners.forEach(fn=>fn({matches:true}));
verify($('#motion-toggle').getAttribute('aria-pressed')==='false','Changing motion preference pauses');
const tr=w.Taster.createTransport({duration:40,loop:true});tr.play();tr.update(45);verify(tr.getState().time===5,'Taster wraps deterministic timeline');tr.pause();tr.update(10);verify(tr.getState().time===5,'Paused transport freezes');tr.seek(40);verify(tr.getState().progress===1,'Seek endpoint exact');
dom.window.close();
const reader=setup('web/index.html','#portada');
reader.load('web/data/libro.js');reader.load('web/assets/js/app.js');
const r$=s=>reader.w.document.querySelector(s);
verify(r$('#capitulo').textContent.includes('El Libro de lo Posible'),'Reader renders real chapter');
verify(r$('#audio').getAttribute('src')===null && r$('#reproductor').hidden,'Revised opening has no stale audio request');
verify(r$('#capitulo img').getAttribute('src')==='assets/art/apertura.svg','Reader selects correct section art');
r$('#buscador').value='metafísica';r$('#buscador').dispatchEvent(new reader.w.Event('input'));
verify([...reader.w.document.querySelectorAll('.indice__item')].some(el=>el.style.display==='none'),'Search filters chapter list');
r$('#boton-tema').click();verify(!reader.w.document.documentElement.classList.contains('dark'),'Theme toggle works');
r$('#boton-menu').click();verify(reader.w.document.activeElement.id==='buscador','Mobile menu focuses search');verify(r$('#lector').inert===true,'Modal background inert');
reader.w.document.dispatchEvent(new reader.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));verify(r$('#lector').inert===false && reader.w.document.activeElement.id==='boton-menu','Escape restores focus');
reader.w.location.hash='#el-lema';reader.w.dispatchEvent(new reader.w.HashChangeEvent('hashchange'));
verify(r$('#capitulo').textContent.includes('El lema'),'Hash navigation renders next chapter');verify(r$('#audio').getAttribute('src').includes('01-el-lema.mp3'),'Unchanged chapter retains online recording');
reader.dom.window.close();
console.log(`OK: ${checks} interaction checks against actual HTML + JS in jsdom. No browser layout claims.`);
