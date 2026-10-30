# Láminas de lo posible

Cuatro ilustraciones originales y una portada editorial, editables y autónomas en SVG. Fondo transparente, lienzo `900 × 700`; pensadas para una superficie `#111613`, con líneas hueso, musgo y oro apagado.

| Archivo | Motivo | Uso |
| --- | --- | --- |
| `cover.svg` | Título y puerta armilar; lienzo 1200 × 630 con fondo oscuro | README y portada editorial |
| `apertura.svg` | Puerta entreabierta dentro de una esfera armilar | Portada y apertura |
| `universales.svg` | Cuatro construcciones sobre un mismo plano | Principios filosóficos |
| `practica.svg` | Compás, plano de medición y escalera | Prácticas revisables |
| `ancoro.svg` | Ciudad imaginaria y archivo abierto | Los Últimos Universales |

Son metáforas visuales, no diagramas científicos ni evidencia de afirmaciones metafísicas. Cada archivo incorpora un título y una descripción accesibles; no requiere fuentes, imágenes ni hojas de estilo externas. Se pueden usar como `<img>` y descargar directamente.

Para regenerar las cuatro láminas (la portada `cover.svg` se mantiene como composición editorial independiente), desde la raíz del repositorio:

```sh
python3 scripts/generate-art.py
```

El generador usa exclusivamente la biblioteca estándar de Python y una semilla fija para los puntos del fondo. Las láminas mantienen la geometría y los colores entre compilaciones. Los nueve símbolos originales del libro se conservan en `simbolos/`.
