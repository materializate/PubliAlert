#!/usr/bin/env python3
"""
parse_epg.py — Convierte raw.xml (EPG TDTChannels) a epg.json
Ejecutado por la GitHub Action update-epg.yml
"""
import xml.etree.ElementTree as ET
import json
import re
import sys
from datetime import datetime, timezone

TARGET_IDS = {
    # Formato .TV (el que usa TDTChannels actualmente)
    'La1.TV', 'La2.TV', 'Antena3.TV', 'Cuatro.TV', 'Telecinco.TV',
    'LaSexta.TV', 'DMax.TV', 'DMAX.TV', 'Mega.TV', 'Neox.TV',
    'FactoriadeFiccion.TV', 'Energy.TV', 'Divinity.TV', 'Bemad.TV',
    # Formato .es (versiones anteriores / alternativas)
    'La1.es', 'La2.es', 'Antena3.es', 'Cuatro.es', 'Telecinco.es',
    'LaSexta.es', 'DMAX.es', 'DMax.es', 'Mega.es', 'Neox.es',
    'FDF.es', 'Energy.es', 'Divinity.es', 'beMad.es', 'BeMad.es',
}

def parse_dt(s):
    """Convierte fecha XMLTV (YYYYMMDDHHMMSS +HHMM) a timestamp Unix."""
    s = s.strip()
    ts = s[:14]
    tz = s[14:].strip()
    dt = datetime(
        int(ts[0:4]), int(ts[4:6]), int(ts[6:8]),
        int(ts[8:10]), int(ts[10:12]), int(ts[12:14])
    )
    sign = -1 if tz and tz[0] == '-' else 1
    h = int(tz[1:3]) if len(tz) >= 3 else 0
    m = int(tz[3:5]) if len(tz) >= 5 else 0
    offset_s = sign * (h * 3600 + m * 60) if tz else 0
    epoch = datetime(1970, 1, 1)
    return int((dt - epoch).total_seconds()) - offset_s

def main():
    print("Leyendo raw.xml...")
    try:
        with open('raw.xml', 'r', encoding='utf-8', errors='replace') as f:
            raw = f.read()
    except FileNotFoundError:
        print("ERROR: raw.xml no encontrado", file=sys.stderr)
        sys.exit(1)

    print(f"Tamaño XML: {len(raw)} chars")
    if len(raw) < 1000:
        print("ERROR: XML demasiado pequeño, posible descarga fallida", file=sys.stderr)
        print("Contenido:", raw[:500])
        sys.exit(1)

    # Sanear & sin escapar que rompen el parser
    raw = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', raw)

    print("Parseando XML...")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"ERROR parseando XML: {e}", file=sys.stderr)
        # Intentar con lxml si está disponible
        try:
            import lxml.etree as lET
            root = lET.fromstring(raw.encode('utf-8'), lET.XMLParser(recover=True))
            print("Parseado con lxml (modo recuperación)")
        except ImportError:
            print("lxml no disponible, fallando", file=sys.stderr)
            sys.exit(1)

    # Ver qué channel IDs hay en el XML para diagnóstico
    all_channels = set()
    for ch_el in root.findall('channel'):
        cid = ch_el.get('id', '')
        if cid:
            all_channels.add(cid)

    print(f"Canales en XML ({len(all_channels)}): {sorted(all_channels)[:20]}")
    matched_targets = TARGET_IDS & all_channels
    print(f"Canales que coinciden con TARGET_IDS: {matched_targets}")

    if not matched_targets:
        # Los IDs no coinciden — añadir todos los que parezcan españoles
        spanish = {c for c in all_channels if any(
            k in c.lower() for k in
            ['antena','telecinco','cuatro','sexta','la1','la2','mega','neox',
             'energy','divinity','bemad','dmax','factoria','fdf']
        )}
        print(f"IDs españoles detectados automáticamente: {spanish}")
        TARGET_IDS.update(spanish)

    result = {}
    count = 0
    skipped = 0

    for prog in root.findall('programme'):
        ch = prog.get('channel', '')
        if ch not in TARGET_IDS:
            skipped += 1
            continue
        start_s = prog.get('start', '')
        stop_s  = prog.get('stop', '')
        el      = prog.find('title')
        title   = el.text.strip() if el is not None and el.text else ''
        if not title or not start_s or not stop_s:
            continue
        try:
            se = parse_dt(start_s)
            ee = parse_dt(stop_s)
        except Exception as ex:
            continue
        if ch not in result:
            result[ch] = []
        result[ch].append({'t': title, 's': se, 'e': ee})
        count += 1

    print(f"Programas procesados: {count} (ignorados: {skipped})")
    print(f"Canales con datos: {list(result.keys())}")

    output = {
        'updated':  int(datetime.now(timezone.utc).timestamp()),
        'count':    count,
        'channels': result,
    }

    with open('epg.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    print(f"epg.json escrito correctamente ({count} programas, {len(result)} canales)")

if __name__ == '__main__':
    main()
