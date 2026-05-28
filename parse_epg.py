#!/usr/bin/env python3
"""
parse_epg.py — Convierte raw.xml (EPG TDTChannels) a epg.json
Usa regex en lugar de XML parser para tolerar XML malformado
"""
import json, re, sys, gzip
from datetime import datetime, timezone

TARGET_IDS = {
    'La1.TV','La2.TV','Antena3.TV','Cuatro.TV','Telecinco.TV',
    'LaSexta.TV','DMax.TV','DMAX.TV','Mega.TV','Neox.TV',
    'FactoriadeFiccion.TV','Energy.TV','Divinity.TV','Bemad.TV',
    'La1.es','La2.es','Antena3.es','Cuatro.es','Telecinco.es',
    'LaSexta.es','DMAX.es','DMax.es','Mega.es','Neox.es',
    'FDF.es','Energy.es','Divinity.es','beMad.es','BeMad.es',
}

def parse_dt(s):
    s = s.strip()
    ts, tz = s[:14], s[14:].strip()
    dt = datetime(int(ts[0:4]),int(ts[4:6]),int(ts[6:8]),
                  int(ts[8:10]),int(ts[10:12]),int(ts[12:14]))
    sign = -1 if tz and tz[0]=='-' else 1
    h = int(tz[1:3]) if len(tz)>=3 else 0
    m = int(tz[3:5]) if len(tz)>=5 else 0
    offset_s = sign*(h*3600+m*60) if tz else 0
    return int((dt-datetime(1970,1,1)).total_seconds())-offset_s

def clean_xml(raw_bytes):
    """Decodifica y limpia el XML de caracteres problemáticos."""
    raw = raw_bytes.decode('utf-8', errors='replace')
    # Eliminar caracteres de control ilegales en XML
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    # Sanear & sin escapar
    raw = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', raw)
    # Eliminar char de reemplazo Unicode
    raw = raw.replace('\ufffd', '')
    return raw

def extract_programs(raw):
    """Extrae programas con regex — tolerante a XML malformado."""
    prog_re  = re.compile(r'<programme\s+([^>]*?)>(.*?)</programme>', re.DOTALL|re.IGNORECASE)
    title_re = re.compile(r'<title[^>]*>(.*?)</title>', re.DOTALL|re.IGNORECASE)
    chan_re   = re.compile(r'\bchannel="([^"]+)"')
    start_re  = re.compile(r'\bstart="([^"]+)"')
    stop_re   = re.compile(r'\bstop="([^"]+)"')

    result = {}
    all_channels = set()
    count = 0

    for m in prog_re.finditer(raw):
        attrs, body = m.group(1), m.group(2)
        ch_m  = chan_re.search(attrs)
        st_m  = start_re.search(attrs)
        sp_m  = stop_re.search(attrs)
        ti_m  = title_re.search(body)
        if not (ch_m and st_m and sp_m and ti_m):
            continue
        ch    = ch_m.group(1).strip()
        title = re.sub(r'<[^>]+>', '', ti_m.group(1).strip())
        title = (title.replace('&amp;','&').replace('&lt;','<')
                      .replace('&gt;','>').replace('&quot;','"').strip())
        all_channels.add(ch)
        if ch not in TARGET_IDS or not title:
            continue
        try:
            se = parse_dt(st_m.group(1))
            ee = parse_dt(sp_m.group(1))
        except:
            continue
        if ch not in result:
            result[ch] = []
        result[ch].append({'t': title, 's': se, 'e': ee})
        count += 1

    return result, all_channels, count

def main():
    # Leer con detección de gzip
    with open('raw.xml','rb') as f:
        header = f.read(3)
    if header[:2] == b'\x1f\x8b':
        print("Detectado gzip — descomprimiendo...")
        with gzip.open('raw.xml','rb') as f:
            raw_bytes = f.read()
    else:
        with open('raw.xml','rb') as f:
            raw_bytes = f.read()

    print(f"Tamanyo: {len(raw_bytes)} bytes")
    raw = clean_xml(raw_bytes)
    print(f"Tamanyo limpio: {len(raw)} chars")

    print("Extrayendo programas con regex...")
    result, all_channels, count = extract_programs(raw)

    print(f"Canales en XML: {sorted(all_channels)[:20]}")
    print(f"Canales con datos: {list(result.keys())}")
    print(f"Programas: {count}")

    # Si no hubo matches, detectar IDs españoles automáticamente
    if not result and all_channels:
        print("Sin matches con TARGET_IDS — detectando canales españoles automáticamente...")
        spanish_kw = ['antena','telecinco','cuatro','sexta','la1','la2','mega',
                      'neox','energy','divinity','bemad','dmax','factoria','fdf','tve']
        spanish = {c for c in all_channels if any(k in c.lower() for k in spanish_kw)}
        print(f"Detectados: {spanish}")
        TARGET_IDS.update(spanish)
        result, _, count = extract_programs(raw)
        print(f"Segunda pasada: {count} programas en {list(result.keys())}")

    output = {
        'updated':  int(datetime.now(timezone.utc).timestamp()),
        'count':    count,
        'channels': result,
    }
    with open('epg.json','w',encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',',':'))

    print(f"epg.json OK: {count} programas, {len(result)} canales")
    if count == 0:
        print("ERROR: 0 programas", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
