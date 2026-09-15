#!/usr/bin/env python3
"""Genera el audio de cada capítulo (voz natural en español) con edge-tts.

Uso:
  python3 web/generar_audio.py                 # genera todos los faltantes
  python3 web/generar_audio.py --desde 14 --hasta 22
  python3 web/generar_audio.py --force         # regenera aunque exista el mp3
  python3 web/generar_audio.py --voz es-MX-DaliaNeural
"""
import os
import sys
import glob
import asyncio

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAIN = os.path.join(ROOT, "web", "data", "plain")
OUT = os.path.join(ROOT, "web", "assets", "audio")

VOZ = "es-MX-DaliaNeural"   # español neutro de América Latina
CHUNK_CHARS = 4200


def chunks_de_texto(texto, n):
    parrafos = texto.split("\n\n")
    chunks, actual = [], ""
    for p in parrafos:
        p = p.strip()
        if not p:
            continue
        if len(actual) + len(p) + 2 > n and actual:
            chunks.append(actual)
            actual = p
        else:
            actual = (actual + "\n\n" + p).strip()
    if actual:
        chunks.append(actual)
    return chunks


async def generar(archivo_txt, archivo_mp3, voz):
    with open(archivo_txt, encoding="utf-8") as fh:
        texto = fh.read().strip()
    if not texto:
        print(f"  [omitido] {os.path.basename(archivo_txt)} vacío")
        return False
    fragmentos = chunks_de_texto(texto, CHUNK_CHARS)
    if len(fragmentos) == 1:
        await edge_tts.Communicate(texto, voz).save(archivo_mp3)
    else:
        tmp_files = []
        for i, frag in enumerate(fragmentos):
            tmp = archivo_mp3 + f".part{i}"
            tmp_files.append(tmp)
            await edge_tts.Communicate(frag, voz).save(tmp)
        with open(archivo_mp3, "wb") as out:
            for tmp in tmp_files:
                with open(tmp, "rb") as f:
                    out.write(f.read())
                os.remove(tmp)
    return True


async def main():
    args = sys.argv[1:]
    solo = int(args[args.index("--solo") + 1]) if "--solo" in args else None
    desde = int(args[args.index("--desde") + 1]) if "--desde" in args else None
    hasta = int(args[args.index("--hasta") + 1]) if "--hasta" in args else None
    voz = args[args.index("--voz") + 1] if "--voz" in args else VOZ
    force = "--force" in args

    os.makedirs(OUT, exist_ok=True)
    archivos = sorted(glob.glob(os.path.join(PLAIN, "*.txt")))
    total = len(archivos)
    hechos, fallidos = 0, []

    for i, archivo_txt in enumerate(archivos, 1):
        nombre = os.path.splitext(os.path.basename(archivo_txt))[0]
        num = int(nombre.split("-", 1)[0])
        if solo is not None and num != solo:
            continue
        if desde is not None and num < desde:
            continue
        if hasta is not None and num > hasta:
            continue
        archivo_mp3 = os.path.join(OUT, nombre + ".mp3")
        if not force and os.path.exists(archivo_mp3) and os.path.getsize(archivo_mp3) > 0:
            print(f"[{i}/{total}] {nombre}  · ya existe")
            hechos += 1
            continue
        print(f"[{i}/{total}] {nombre}  · generando…", flush=True)
        try:
            if await generar(archivo_txt, archivo_mp3, voz):
                hechos += 1
                print(f"           → OK ({os.path.getsize(archivo_mp3)//1024} KB)", flush=True)
            else:
                fallidos.append(nombre)
        except Exception as e:  # noqa: BLE001
            fallidos.append(nombre)
            print(f"           → ERROR: {e}", flush=True)

    print(f"\nListo. Generados/saltados: {hechos}. Fallidos: {len(fallidos)}")
    if fallidos:
        print("Fallidos:", ", ".join(fallidos))


if __name__ == "__main__":
    asyncio.run(main())