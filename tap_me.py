# This is an open-source file, property of Argon Intelligence - ARGOSINT. Its sale is prohibited. It is a basic project generated 50/50 with artificial intelligence models, so extremely professional performance is not expected. Use the code responsibly only. If you want to support the project with an improved version, do not hesitate to contact us.
import argparse
import json
import re
import secrets
import socket
import struct
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote


MODELOS_RAW = [
    ("iPhone (1.ª gen.)", 2007, 115.0, 61.0, 11.6, 1),
    ("iPhone 3G", 2008, 115.5, 62.1, 12.3, 1),
    ("iPhone 3GS", 2009, 115.5, 62.1, 12.3, 1),
    ("iPhone 4", 2010, 115.2, 58.6, 9.3, 1),
    ("iPhone 4s", 2011, 115.2, 58.6, 9.3, 1),
    ("iPhone 5", 2012, 123.8, 58.6, 7.6, 1),
    ("iPhone 5c", 2013, 124.4, 59.2, 8.97, 1),
    ("iPhone 5s", 2013, 123.8, 58.6, 7.6, 1),
    ("iPhone 6", 2014, 138.1, 67.0, 6.9, 1),
    ("iPhone 6 Plus", 2014, 158.1, 77.8, 7.1, 1),
    ("iPhone 6s", 2015, 138.3, 67.1, 7.1, 1),
    ("iPhone 6s Plus", 2015, 158.2, 77.9, 7.3, 1),
    ("iPhone SE (1.ª gen.)", 2016, 123.8, 58.6, 7.6, 1),
    ("iPhone 7", 2016, 138.3, 67.1, 7.1, 1),
    ("iPhone 7 Plus", 2016, 158.2, 77.9, 7.3, 2),
    ("iPhone 8", 2017, 138.4, 67.3, 7.3, 1),
    ("iPhone 8 Plus", 2017, 158.4, 78.1, 7.5, 2),
    ("iPhone X", 2017, 143.6, 70.9, 7.7, 2),
    ("iPhone XS", 2018, 143.6, 70.9, 7.7, 2),
    ("iPhone XS Max", 2018, 157.5, 77.4, 7.7, 2),
    ("iPhone XR", 2018, 150.9, 75.7, 8.3, 1),
    ("iPhone 11", 2019, 150.9, 75.7, 8.3, 2),
    ("iPhone 11 Pro", 2019, 144.0, 71.4, 8.1, 3),
    ("iPhone 11 Pro Max", 2019, 158.0, 77.8, 8.1, 3),
    ("iPhone SE (2.ª gen.)", 2020, 138.4, 67.3, 7.3, 1),
    ("iPhone 12 mini", 2020, 131.5, 64.2, 7.4, 2),
    ("iPhone 12", 2020, 146.7, 71.5, 7.4, 2),
    ("iPhone 12 Pro", 2020, 146.7, 71.5, 7.4, 3),
    ("iPhone 12 Pro Max", 2020, 160.8, 78.1, 7.4, 3),
    ("iPhone 13 mini", 2021, 131.5, 64.2, 7.65, 2),
    ("iPhone 13", 2021, 146.7, 71.5, 7.65, 2),
    ("iPhone 13 Pro", 2021, 146.7, 71.5, 7.65, 3),
    ("iPhone 13 Pro Max", 2021, 160.8, 78.1, 7.65, 3),
    ("iPhone SE (3.ª gen.)", 2022, 138.4, 67.3, 7.3, 1),
    ("iPhone 14", 2022, 146.7, 71.5, 7.8, 2),
    ("iPhone 14 Plus", 2022, 160.8, 78.1, 7.8, 2),
    ("iPhone 14 Pro", 2022, 147.5, 71.5, 7.85, 3),
    ("iPhone 14 Pro Max", 2022, 160.7, 77.6, 7.85, 3),
    ("iPhone 15", 2023, 147.6, 71.6, 7.8, 2),
    ("iPhone 15 Plus", 2023, 160.9, 77.8, 7.8, 2),
    ("iPhone 15 Pro", 2023, 146.6, 70.6, 8.25, 3),
    ("iPhone 15 Pro Max", 2023, 159.9, 76.7, 8.25, 3),
    ("iPhone 16", 2024, 147.6, 71.6, 7.8, 2),
    ("iPhone 16 Plus", 2024, 160.9, 77.8, 7.8, 2),
    ("iPhone 16 Pro", 2024, 149.6, 71.5, 8.25, 3),
    ("iPhone 16 Pro Max", 2024, 163.0, 77.6, 8.25, 3),
    ("iPhone 16e", 2025, 146.7, 71.5, 7.8, 1),
    ("iPhone 17", 2025, 149.6, 71.5, 7.95, 2),
    ("iPhone Air", 2025, 156.2, 74.7, 5.64, 1),
    ("iPhone 17 Pro", 2025, 150.0, 71.9, 8.75, 3),
    ("iPhone 17 Pro Max", 2025, 163.4, 78.0, 8.75, 3),
    ("iPhone 17e", 2026, 146.7, 71.5, 7.8, 1),
    ("iPhone 18 Pro", 2026, 150.0, 71.9, 8.75, 3),
    ("iPhone 18 Pro Max", 2026, 163.4, 78.0, 8.75, 3),
]

FUENTE_MODELOS = (
    "Especificaciones nominales de Apple. Contraste: Wikipedia, 'List of iPhone "
    "models' (sept. 2026). Los modelos plegables no se incluyen."
)


def _slug(nombre, anio):
    s = re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")
    return "%s-%d" % (s, anio)


MODELOS = [
    {
        "id": _slug(n, a),
        "nombre": n,
        "anio": a,
        "alto": h,
        "ancho": w,
        "grosor": d,
        "camaras": c,
    }
    for (n, a, h, w, d, c) in MODELOS_RAW
]


MAX_BYTES = 60 * 1024 * 1024
MAX_FOTOS = 16
FOTOS = {}
_BLOQUEO = threading.Lock()


def tipo_imagen(b):
    if b[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "image/webp"
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if b[4:8] == b"ftyp" and b[8:12] in (b"heic", b"heix", b"mif1", b"heim", b"hevc"):
        return "image/heic"
    return None


_TAM_TIPO = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}


def _leer_tiff(t):
    if t[:2] == b"II":
        e = "<"
    elif t[:2] == b"MM":
        e = ">"
    else:
        return {}
    if struct.unpack(e + "H", t[2:4])[0] != 42:
        return {}

    def ifd(off):
        res = {}
        n = struct.unpack(e + "H", t[off:off + 2])[0]
        for k in range(n):
            b = off + 2 + 12 * k
            tag, typ, cnt = struct.unpack(e + "HHI", t[b:b + 8])
            tam = _TAM_TIPO.get(typ, 1) * cnt
            if tam <= 4:
                dato = t[b + 8:b + 8 + tam]
            else:
                o = struct.unpack(e + "I", t[b + 8:b + 12])[0]
                dato = t[o:o + tam]
            res[tag] = (typ, cnt, dato)
        return res

    def valor(ent):
        typ, _cnt, d = ent
        if typ == 2:
            return d.split(b"\x00")[0].decode("latin-1").strip()
        if typ == 3:
            return struct.unpack(e + "H", d[:2])[0]
        if typ == 4:
            return struct.unpack(e + "I", d[:4])[0]
        if typ == 5:
            n, dn = struct.unpack(e + "II", d[:8])
            return (n / dn) if dn else None
        return None

    out = {}
    off0 = struct.unpack(e + "I", t[4:8])[0]
    i0 = ifd(off0)
    if 0x010F in i0:
        out["marca"] = valor(i0[0x010F])
    if 0x0110 in i0:
        out["modelo"] = valor(i0[0x0110])
    if 0x0112 in i0:
        out["orientacion"] = valor(i0[0x0112])
    if 0x8769 in i0:
        ie = ifd(valor(i0[0x8769]))
        if 0x920A in ie:
            out["focal_mm"] = valor(ie[0x920A])
        if 0xA405 in ie:
            out["focal_35mm"] = valor(ie[0xA405])
        if 0x9003 in ie:
            out["fecha"] = valor(ie[0x9003])
    return out


def leer_exif(datos):
    try:
        if datos[:2] != b"\xff\xd8":
            return {}
        i = 2
        while i + 4 <= len(datos):
            if datos[i] != 0xFF:
                break
            m = datos[i + 1]
            if m in (0xD9, 0xDA):
                break
            if 0xD0 <= m <= 0xD7 or m == 0x01:
                i += 2
                continue
            (largo,) = struct.unpack(">H", datos[i + 2:i + 4])
            if m == 0xE1 and datos[i + 4:i + 10] == b"Exif\x00\x00":
                return _leer_tiff(datos[i + 10:i + 2 + largo])
            i += 2 + largo
    except Exception:
        pass
    return {}


class Manejador(BaseHTTPRequestHandler):
    server_version = "AltimetroIPhone/1.0"

    def log_message(self, fmt, *args):
        pass

    def _enviar(self, codigo, cuerpo, tipo, cache=False):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, obj, codigo=200):
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8")

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta in ("/", "/index.html"):
            self._enviar(200, PAGINA.encode("utf-8"), "text/html; charset=utf-8")
        elif ruta == "/api/modelos":
            self._json({"modelos": MODELOS, "fuente": FUENTE_MODELOS})
        elif ruta.startswith("/api/foto/"):
            fid = ruta.rsplit("/", 1)[-1]
            with _BLOQUEO:
                ent = FOTOS.get(fid)
            if not ent:
                self._enviar(404, b"No encontrada", "text/plain; charset=utf-8")
            else:
                self._enviar(200, ent[1], ent[0], cache=True)
        else:
            self._enviar(404, b"No encontrado", "text/plain; charset=utf-8")

    def do_POST(self):
        ruta = self.path.split("?")[0]
        if ruta != "/api/foto":
            self._enviar(404, b"No encontrado", "text/plain; charset=utf-8")
            return
        try:
            largo = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            largo = 0
        if largo <= 0:
            self._enviar(400, "Cuerpo vacío".encode("utf-8"), "text/plain; charset=utf-8")
            return
        if largo > MAX_BYTES:
            self._enviar(413, "Imagen demasiado grande (máx. 60 MB)".encode("utf-8"),
                         "text/plain; charset=utf-8")
            return
        datos = self.rfile.read(largo)
        tipo = tipo_imagen(datos)
        if tipo is None:
            self._enviar(415, "Formato no reconocido. Usa JPEG, PNG, WebP o GIF.".encode("utf-8"),
                         "text/plain; charset=utf-8")
            return
        if tipo == "image/heic":
            self._enviar(415, "HEIC no es compatible con el navegador. Exporta a JPEG o PNG.".encode("utf-8"),
                         "text/plain; charset=utf-8")
            return
        nombre = unquote(self.headers.get("X-Nombre", "imagen"))[:120]
        fid = secrets.token_hex(8)
        with _BLOQUEO:
            FOTOS[fid] = (tipo, datos, nombre)
            while len(FOTOS) > MAX_FOTOS:
                FOTOS.pop(next(iter(FOTOS)))
        exif = leer_exif(datos) if tipo == "image/jpeg" else {}
        self._json({"id": fid, "bytes": len(datos), "tipo": tipo, "nombre": nombre, "exif": exif})


def _puerto_libre(host, preferido):
    for p in range(preferido, preferido + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, p))
                return p
            except OSError:
                continue
    raise SystemExit("No hay puertos libres cerca de %d" % preferido)


def main():
    ap = argparse.ArgumentParser(description="Altímetro iPhone: medida de alturas con referencia conocida")
    ap.add_argument("--host", default="127.0.0.1", help="interfaz de escucha (por defecto 127.0.0.1)")
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--no-abrir", action="store_true", help="no abrir el navegador automáticamente")
    a = ap.parse_args()
    puerto = _puerto_libre(a.host, a.puerto)
    srv = ThreadingHTTPServer((a.host, puerto), Manejador)
    url = "http://%s:%d/" % (a.host, puerto)
    print("ALTÍMETRO IPHONE  ·  %s" % url)
    print("Ctrl+C para detener.")
    if not a.no_abrir:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        srv.server_close()


PAGINA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Altímetro iPhone</title>
<style>
:root{--bg:#0a0d10;--panel:#10151a;--panel2:#141a20;--line:#1f2830;--line2:#2c3742;--txt:#d3dbe1;--mut:#7a8793;
--acc:#e0a526;--ref:#5ec2b7;--warn:#e0653a;--ok:#7fb069;--hor:#8fa8ff;
--mono:ui-monospace,"SF Mono","JetBrains Mono",Consolas,"Liberation Mono",monospace;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--txt);font:13px/1.45 var(--sans);overflow:hidden}
.top{height:54px;display:flex;align-items:center;gap:28px;padding:0 18px;border-bottom:1px solid var(--line);background:var(--panel)}
.brand{display:flex;align-items:baseline;white-space:nowrap}
.brand b{letter-spacing:.3em;font-size:12px}
.brand i{font-style:normal;color:var(--mut);font-size:11px;margin-left:14px;letter-spacing:.04em}
.modes{display:flex;border:1px solid var(--line2);border-radius:2px}
.modes button{background:transparent;border:0;border-right:1px solid var(--line2);color:var(--mut);padding:8px 16px;font:600 11px var(--sans);letter-spacing:.14em;cursor:pointer}
.modes button:last-child{border-right:0}
.modes button:hover{color:var(--txt)}
.modes button.on{color:var(--bg);background:var(--acc)}
.readout{margin-left:auto;display:flex;align-items:baseline;gap:14px;white-space:nowrap}
.readout .lbl{font:600 10px var(--sans);letter-spacing:.2em;color:var(--mut)}
.readout .val{font:600 28px var(--mono);color:var(--acc);min-width:150px;text-align:right}
.readout .sub{font:11px var(--mono);color:var(--mut);min-width:170px}
.shell{display:grid;grid-template-columns:372px 1fr;height:calc(100% - 54px)}
.panel{overflow-y:auto;border-right:1px solid var(--line);background:var(--panel)}
.blk{padding:14px 16px 12px;border-bottom:1px solid var(--line)}
.blk h3{margin:0 0 10px;font:600 10.5px var(--sans);letter-spacing:.2em;color:var(--mut);display:flex;align-items:center;gap:10px}
.blk h3 .n{color:var(--acc);font-family:var(--mono);letter-spacing:.05em}
.row{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0;align-items:center}
.btn{background:transparent;border:1px solid var(--line2);color:var(--txt);padding:7px 10px;font:600 10.5px var(--sans);letter-spacing:.1em;cursor:pointer;border-radius:2px}
.btn:hover{border-color:var(--mut)}
.btn.on{border-color:var(--acc);color:var(--acc);background:rgba(224,165,38,.08)}
.btn:disabled{opacity:.35;cursor:not-allowed}
.inp{width:100%;background:var(--bg);border:1px solid var(--line2);color:var(--txt);padding:7px 8px;font:12px var(--mono);border-radius:2px;outline:none}
.inp:focus{border-color:var(--acc)}
.inp.sm{width:92px;text-align:right}
.fl{display:block;margin:8px 0 4px;font:600 10px var(--sans);letter-spacing:.14em;color:var(--mut)}
.chk{display:flex;align-items:center;gap:7px;color:var(--mut);font-size:12px;margin:6px 0}
.chk input{accent-color:var(--acc)}
.kv{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:4px 0;border-bottom:1px dotted var(--line);font:12px var(--mono)}
.kv span{color:var(--mut);font:600 10px var(--sans);letter-spacing:.08em}
.kv b{font-weight:500;text-align:right}
.kv b.warn{color:var(--warn)}.kv b.ok{color:var(--ok)}.kv b.acc{color:var(--acc)}
.note{color:var(--mut);font-size:11px;line-height:1.5;margin:6px 0}
.pins{width:100%;border-collapse:collapse;font:11.5px var(--mono);margin-top:8px}
.pins th{font:600 9.5px var(--sans);letter-spacing:.12em;color:var(--mut);text-align:right;padding:3px 4px;border-bottom:1px solid var(--line2)}
.pins th:first-child,.pins td:first-child{text-align:left}
.pins td{text-align:right;padding:4px;border-bottom:1px dotted var(--line)}
.pins td button{background:none;border:0;color:var(--mut);cursor:pointer;font:12px var(--mono)}
.pins td button:hover{color:var(--warn)}
.list{font:11.5px var(--mono);margin-top:6px}
.list div{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dotted var(--line)}
.list button{background:none;border:0;color:var(--mut);cursor:pointer}
.list button:hover{color:var(--warn)}
.stage{position:relative;background:#06080a;overflow:hidden;
background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:32px 32px;background-position:-1px -1px}
#cv{position:absolute;inset:0;display:block;touch-action:none}
.hint{position:absolute;left:146px;bottom:12px;max-width:calc(100% - 180px);padding:7px 11px;background:rgba(10,13,16,.9);border:1px solid var(--line2);font:11px var(--mono);color:var(--mut);pointer-events:none}
.hint b{color:var(--acc);font-weight:600}
.loupe{position:absolute;top:12px;right:12px;width:142px;height:142px;border:1px solid var(--line2);background:var(--bg);display:none;pointer-events:none}
.loupe canvas{display:block}
.drop{position:absolute;left:132px;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;pointer-events:none}
.drop div{border:1px dashed var(--line2);padding:36px 54px;text-align:center;color:var(--mut);font:600 11px var(--sans);letter-spacing:.18em;line-height:2;background:rgba(10,13,16,.7)}
.drop.over div{border-color:var(--acc);color:var(--acc)}
.err{color:var(--warn);font:11.5px var(--mono);margin:6px 0;min-height:14px}
::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{background:var(--line2)}::-webkit-scrollbar-track{background:var(--panel)}
@media (max-width:980px){.shell{grid-template-columns:320px 1fr}.brand i{display:none}.readout .sub{display:none}}
</style>
</head>
<body>
<header class="top">
  <div class="brand"><b>ALTÍMETRO</b><i>REFERENCIA iPHONE · METROLOGÍA MONOCULAR</i></div>
  <nav class="modes" id="modes">
    <button data-mode="plano" class="on">PLANO ÚNICO</button>
    <button data-mode="persp">PERSPECTIVA</button>
    <button data-mode="manual">MANUAL</button>
  </nav>
  <div class="readout"><span class="lbl">ALTURA</span><span class="val" id="roVal">—</span><span class="sub" id="roSub"></span></div>
</header>
<div class="shell">
<aside class="panel" id="panel">

  <section class="blk">
    <h3><span class="n">01</span>FOTOGRAFÍA</h3>
    <div class="row"><button class="btn" id="bFile">CARGAR IMAGEN</button><input type="file" id="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden></div>
    <div class="err" id="err"></div>
    <div class="kv"><span>ARCHIVO</span><b id="kName">—</b></div>
    <div class="kv"><span>RESOLUCIÓN</span><b id="kRes">—</b></div>
    <div class="kv"><span>EXIF · DISPOSITIVO</span><b id="kCam">—</b></div>
  </section>

  <section class="blk">
    <h3><span class="n">02</span>REFERENCIA · iPHONE</h3>
    <label class="fl">MODELO</label>
    <select id="model" class="inp"></select>
    <label class="chk"><input type="checkbox" id="only3"> Solo triple cámara</label>
    <div class="row">
      <button class="btn" data-tool="contour">TRAZAR CONTORNO</button>
      <button class="btn" id="bUndo">DESHACER</button>
      <button class="btn" id="bClearC">BORRAR</button>
    </div>
    <div class="kv"><span>DIMENSIÓN NOMINAL</span><b id="kNom">—</b></div>
    <div class="kv"><span>LONGITUD DEL EJE</span><b id="kL">—</b></div>
    <div class="kv"><span>ANCHURA</span><b id="kW">—</b></div>
    <div class="kv"><span>RELACIÓN A/L vs NOMINAL</span><b id="kAsp">—</b></div>
    <div class="kv"><span>INCLINACIÓN DEL EJE</span><b id="kTilt">—</b></div>
    <div class="kv"><span>ESCALA EN SU PLANO</span><b id="kScale">—</b></div>
  </section>

  <section class="blk">
    <h3><span class="n">03</span>SUJETO · SUELO</h3>
    <div class="row"><button class="btn" data-tool="floor">MARCAR SUELO (PIES)</button></div>
    <div class="kv"><span>POSICIÓN (px)</span><b id="kFloor">—</b></div>
  </section>

  <section class="blk" id="secPersp" style="display:none">
    <h3><span class="n">04</span>PERSPECTIVA</h3>
    <div class="kv"><span>FOCAL EQUIV. 35 mm</span><input id="f35" type="number" class="inp sm" min="8" max="400" step="0.5" value="26"></div>
    <div class="note" id="f35note"></div>
    <label class="fl">HORIZONTE</label>
    <select id="horMode" class="inp">
      <option value="level">Horizontal · 1 clic</option>
      <option value="free">Inclinado · 2 clics</option>
      <option value="vp">Por paralelas · 4 líneas</option>
    </select>
    <div class="row"><button class="btn" data-tool="horizon">FIJAR HORIZONTE</button></div>
    <div class="kv" id="rowHorY"><span>HORIZONTE · Y (px)</span><input id="horY" type="number" class="inp sm" step="1"></div>
    <div class="row">
      <button class="btn" data-tool="refFoot">BASE DEL iPHONE EN EL SUELO</button>
    </div>
    <label class="chk"><input type="checkbox" id="link"> iPhone en el mismo plano que el sujeto</label>
    <div class="row"><button class="btn" data-tool="ground">PUNTOS EN EL SUELO</button><button class="btn" id="bClearG">LIMPIAR</button></div>
    <div class="kv"><span>CABECEO DE CÁMARA</span><b id="kPitch">—</b></div>
    <div class="kv"><span>ALTURA DE CÁMARA</span><b id="kHc">—</b></div>
    <div class="kv"><span>DIST. HORIZONTAL iPHONE</span><b id="kDr">—</b></div>
    <div class="kv"><span>DIST. HORIZONTAL SUJETO</span><b id="kDs">—</b></div>
    <div class="kv"><span>PROFUNDIDAD SUJETO / iPHONE</span><b id="kRatio">—</b></div>
    <div class="list" id="gList"></div>
  </section>

  <section class="blk" id="secMan" style="display:none">
    <h3><span class="n">05</span>MANUAL</h3>
    <div class="row">
      <button class="btn" data-tool="ruler">REGLA</button>
      <button class="btn" data-tool="curve">CURVA</button>
      <button class="btn" data-tool="copy">COLOCAR iPHONE</button>
    </div>
    <label class="chk"><input type="checkbox" id="smooth" checked> Curva suavizada (spline)</label>
    <label class="fl">ESCALA DEL PLANO</label>
    <select id="manPlane" class="inp"><option value="ref">Plano del iPhone de referencia</option><option value="sub">Plano del sujeto (requiere perspectiva)</option></select>
    <label class="fl">MODELO DE LA COPIA</label>
    <select id="copyModel" class="inp"></select>
    <div class="note">Copia seleccionada: <b>Q / E</b> gira 1° (Mayús: 15°), <b>Supr</b> elimina. Curva: Intro o doble clic para terminar.</div>
    <div class="list" id="mList"></div>
    <div class="row"><button class="btn" id="bClearM">LIMPIAR MANUAL</button></div>
  </section>

  <section class="blk">
    <h3><span class="n">06</span>MEDICIÓN</h3>
    <div class="row"><button class="btn" data-tool="measure">MEDIR · CLIC PARA FIJAR</button><button class="btn" id="bClearP">LIMPIAR</button></div>
    <div class="kv"><span>LECTURA · PLANO ÚNICO</span><b id="lvPlano">—</b></div>
    <div class="kv"><span>LECTURA · PERSPECTIVA</span><b id="lvPersp">—</b></div>
    <div class="kv"><span>DIFERENCIA</span><b id="lvDiff">—</b></div>
    <div class="kv"><span>EN UNIDADES DE iPHONE</span><b id="lvUnits">—</b></div>
    <table class="pins" id="pinTable"></table>
  </section>

  <section class="blk">
    <h3><span class="n">07</span>PARÁMETROS Y EXPORTACIÓN</h3>
    <div class="kv"><span>σ DE CLIC (px)</span><input id="sigma" type="number" class="inp sm" min="0.2" max="20" step="0.1" value="2"></div>
    <div class="row"><button class="btn" id="bJson">EXPORTAR JSON</button><button class="btn" id="bPng">EXPORTAR PNG</button></div>
    <div class="note" id="srcNote"></div>
    <div class="note">La desviación típica se obtiene por Monte Carlo sobre los puntos marcados y la focal (3 %). No contempla errores sistemáticos: distorsión de lente, iPhone inclinado hacia la cámara, suelo irregular o postura del sujeto.</div>
  </section>
</aside>

<section class="stage" id="stage">
  <canvas id="cv"></canvas>
  <div class="drop" id="drop"><div>ARRASTRA UNA FOTOGRAFÍA<br>O PULSA «CARGAR IMAGEN»</div></div>
  <div class="hint" id="hint"></div>
  <div class="loupe" id="loupe"><canvas id="lp" width="140" height="140"></canvas></div>
</section>
</div>

<script>
'use strict';
/*GEO-BEGIN*/
/* ============================================================================
   NÚCLEO GEOMÉTRICO (puro, sin DOM). Unidades internas: Hc = 1 (altura de cámara).
   Sistema de cámara: x derecha, y abajo, z hacia delante.
   ========================================================================== */
const Geo=(()=>{
  const dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const add=(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]];
  const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
  const mul=(a,s)=>[a[0]*s,a[1]*s,a[2]*s];
  const len=a=>Math.hypot(a[0],a[1],a[2]);
  /* par: {w,h,f35,l}. l = línea del horizonte en coordenadas homogéneas de imagen.
     Normal del suelo (hacia arriba) en el sistema de cámara: u ∝ Kᵀ l. */
  function camera(par){
    if(!par||!par.l) return null;
    const f=par.f35*Math.max(par.w,par.h)/36, cx=par.w/2, cy=par.h/2;
    const n2=Math.hypot(par.l[0],par.l[1]); if(!(n2>1e-12)) return null;
    const l=[par.l[0]/n2,par.l[1]/n2,par.l[2]/n2];
    let u=[f*l[0],f*l[1],cx*l[0]+cy*l[1]+l[2]];
    const n=len(u); if(!(n>1e-12)) return null;
    u=mul(u,1/n); if(u[1]>0) u=mul(u,-1);
    return {f,cx,cy,u,l};
  }
  const ray=(c,p)=>[(p.x-c.cx)/c.f,(p.y-c.cy)/c.f,1];
  /* Intersección del rayo con el suelo (u·X = -Hc, Hc=1). Requiere píxel bajo el horizonte. */
  function groundPoint(c,p){
    if(!p) return null;
    const r=ray(c,p), d=dot(c.u,r);
    if(!(d<-1e-6)) return null;
    return mul(r,-1/d);
  }
  /* Plano vertical "de cartelera" por un punto de apoyo: perpendicular a la dirección horizontal cámara-punto. */
  function vplane(c,foot){
    const G=groundPoint(c,foot); if(!G) return null;
    const Gh=add(G,c.u), dh=len(Gh); if(!(dh>1e-9)) return null;
    return {G,nh:mul(Gh,1/dh),dh};
  }
  function onPlane(c,pl,p){
    if(!p||!pl) return null;
    const r=ray(c,p), den=dot(r,pl.nh);
    if(!(den>1e-9)) return null;
    return mul(r,pl.dh/den);
  }
  const heightU=(c,X)=>dot(c.u,X)+1;
  const project=(c,X)=>({x:c.f*X[0]/X[2]+c.cx,y:c.f*X[1]/X[2]+c.cy});
  /* inp: {w,h,f35,l,Lmm,A,B,floorP,refFoot}. A,B = extremos del eje del iPhone. */
  function solve(inp){
    if(!inp||!inp.A||!inp.B||!inp.floorP||!inp.refFoot) return null;
    const cam=camera(inp); if(!cam) return null;
    const plS=vplane(cam,inp.floorP), plR=vplane(cam,inp.refFoot); if(!plS||!plR) return null;
    const XA=onPlane(cam,plR,inp.A), XB=onPlane(cam,plR,inp.B); if(!XA||!XB) return null;
    const d=len(sub(XA,XB)); if(!(d>1e-9)) return null;
    return {cam,plS,plR,XA,XB,Hc:inp.Lmm/d};
  }
  function heightAt(sol,p){
    const X=onPlane(sol.cam,sol.plS,p); if(!X) return null;
    return heightU(sol.cam,X)*sol.Hc;
  }
  function groundMM(sol,p){const G=groundPoint(sol.cam,p);return G?mul(G,sol.Hc):null;}
  const pitchDeg=c=>Math.atan2(c.u[2],-c.u[1])*180/Math.PI;
  const rollDeg=c=>Math.abs(c.l[1])<1e-12?90:Math.atan(-c.l[0]/c.l[1])*180/Math.PI;
  /* Dirección en imagen (hacia arriba) de una vertical 3D que pasa por el píxel p. */
  function vdir(c,p){
    const vz=c.u[2], vx=c.f*c.u[0]+c.cx*vz, vy=c.f*c.u[1]+c.cy*vz;
    if(Math.abs(vz)>1e-6){
      let d=[vx/vz-p.x,vy/vz-p.y]; const n=Math.hypot(d[0],d[1])||1; d=[d[0]/n,d[1]/n];
      return vz<0?[-d[0],-d[1]]:d;
    }
    const n=Math.hypot(vx,vy)||1; return [vx/n,vy/n];
  }
  return {camera,groundPoint,vplane,onPlane,heightU,project,solve,heightAt,groundMM,pitchDeg,rollDeg,vdir,cross,add,sub,mul,len,dot};
})();
/*GEO-END*/

/* ======================= utilidades ======================= */
const $=id=>document.getElementById(id);
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const fmt=(v,d=1)=>(v==null||!isFinite(v))?'—':v.toLocaleString('es-ES',{minimumFractionDigits:d,maximumFractionDigits:d,useGrouping:false});
const fmtLen=mm=>mm==null||!isFinite(mm)?'—':(Math.abs(mm)>=2000?fmt(mm/1000,2)+' m':fmt(mm/10,1)+' cm');
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function gauss(r){let u=0;while(u===0)u=r();const v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function stdev(a){const n=a.length;if(n<2)return null;const m=a.reduce((s,x)=>s+x,0)/n;return Math.sqrt(a.reduce((s,x)=>s+(x-m)*(x-m),0)/(n-1));}

const G=132;
const MONO='ui-monospace,"SF Mono",Consolas,monospace';
const C={bg:'#06080a',panel:'#10151a',line:'#1f2830',line2:'#2c3742',txt:'#d3dbe1',mut:'#7a8793',acc:'#e0a526',ref:'#5ec2b7',warn:'#e0653a',ok:'#7fb069',hor:'#8fa8ff'};

/* ======================= estado ======================= */
const S={
  img:null,w:0,h:0,photo:null,exif:{},name:'',
  mode:'plano',tool:'contour',
  models:[],modelId:'',fuente:'',
  contour:{pts:[],closed:false},
  floor:null,
  persp:{horMode:'level',h1:null,h2:null,vl:[],f35:26,f35src:'valor por defecto',refFoot:null,link:false},
  ground:[],gdraft:null,
  pins:[],
  man:{rulers:[],curves:[],copies:[],sel:null,smooth:true,plane:'ref',copyModel:''},
  draft:null,
  sigma:2,
  view:{k:1,tx:0,ty:0},viewSet:false,
  mouse:null,space:false,panning:false,
  m:null,sPlane:null,pm:null,crop:null,cropDirty:false
};
const cv=$('cv'),ctx=cv.getContext('2d');
let DPR=1;
const refModel=()=>S.models.find(m=>m.id===S.modelId)||null;
const modelById=id=>S.models.find(m=>m.id===id)||null;

/* ======================= transformaciones ======================= */
const i2s=p=>({x:p.x*S.view.k+S.view.tx,y:p.y*S.view.k+S.view.ty});
const s2i=p=>({x:(p.x-S.view.tx)/S.view.k,y:(p.y-S.view.ty)/S.view.k});
function evPos(e){const r=cv.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};}

/* ======================= contorno: métricas =======================
   Momentos de área del polígono (Green). Eje principal = autovector mayor. */
/*METRICS-BEGIN*/
function contourMetricsOf(pts){
  const n=pts.length; if(n<3) return null;
  let A2=0,Sx=0,Sy=0,Jxx=0,Jyy=0,Jxy=0;
  for(let i=0;i<n;i++){
    const p=pts[i],q=pts[(i+1)%n],cr=p.x*q.y-q.x*p.y;
    A2+=cr; Sx+=(p.x+q.x)*cr; Sy+=(p.y+q.y)*cr;
    Jyy+=cr*(p.x*p.x+p.x*q.x+q.x*q.x);
    Jxx+=cr*(p.y*p.y+p.y*q.y+q.y*q.y);
    Jxy+=cr*(p.x*q.y+2*p.x*p.y+2*q.x*q.y+q.x*p.y);
  }
  const A=A2/2; if(Math.abs(A)<1e-6) return null;
  const cx=Sx/(6*A),cy=Sy/(6*A);
  const mxx=Jyy/(12*A)-cx*cx, myy=Jxx/(12*A)-cy*cy, mxy=Jxy/(24*A)-cx*cy;
  const th=0.5*Math.atan2(2*mxy,mxx-myy);
  let ax=Math.cos(th),ay=Math.sin(th);
  if(ay>0||(Math.abs(ay)<1e-12&&ax<0)){ax=-ax;ay=-ay;}
  const ex=-ay,ey=ax;
  let amax=-Infinity,amin=Infinity,emax=-Infinity,emin=Infinity;
  for(const p of pts){
    const sa=(p.x-cx)*ax+(p.y-cy)*ay, se=(p.x-cx)*ex+(p.y-cy)*ey;
    if(sa>amax)amax=sa; if(sa<amin)amin=sa; if(se>emax)emax=se; if(se<emin)emin=se;
  }
  return {area:Math.abs(A),cx,cy,ax,ay,ex,ey,amax,amin,emax,emin,L:amax-amin,W:emax-emin,
    A:{x:cx+ax*amin,y:cy+ay*amin},B:{x:cx+ax*amax,y:cy+ay*amax},
    tilt:Math.atan2(ax,-ay)*180/Math.PI};
}
/*METRICS-END*/
function contourMetrics(){return S.contour.closed?contourMetricsOf(S.contour.pts):null;}

/* ======================= recorte del iPhone (para la escala) ======================= */
function buildCrop(){
  const m=S.m;
  if(!m||!S.img){S.crop=null;return;}
  const sc=Math.min(1,700/m.L);
  const cw=Math.max(2,Math.ceil(m.W*sc)),ch=Math.max(2,Math.ceil(m.L*sc));
  const c=document.createElement('canvas');c.width=cw;c.height=ch;
  const g=c.getContext('2d');
  g.setTransform(sc*m.ex,-sc*m.ax,sc*m.ey,-sc*m.ay,sc*(-m.ex*m.cx-m.ey*m.cy-m.emin),sc*(m.ax*m.cx+m.ay*m.cy+m.amax));
  g.beginPath();S.contour.pts.forEach((p,i)=>i?g.lineTo(p.x,p.y):g.moveTo(p.x,p.y));g.closePath();g.clip();
  g.drawImage(S.img,0,0);
  S.crop={cv:c,cw,ch,sc};
}

/* ======================= entradas del modelo ======================= */
function horizonL(J){
  J=J||(p=>p);
  const P=S.persp;
  if(P.horMode==='vp'){
    if(P.vl.length<4) return null;
    const hl=P.vl.map(l=>{const a=J(l.a),b=J(l.b);return Geo.cross([a.x,a.y,1],[b.x,b.y,1]);});
    const v1=Geo.cross(hl[0],hl[1]),v2=Geo.cross(hl[2],hl[3]);
    const l=Geo.cross(v1,v2);
    return Math.hypot(l[0],l[1])>1e-9*Math.max(1,Math.abs(l[2]))?l:null;
  }
  if(P.horMode==='level'){ if(!P.h1) return null; return [0,1,-J(P.h1).y]; }
  if(!P.h1||!P.h2) return null;
  const a=J(P.h1),b=J(P.h2);
  return Geo.cross([a.x,a.y,1],[b.x,b.y,1]);
}
function baseInputs(){
  const m=S.m,model=refModel();
  if(!m||!model||!S.floor) return null;
  return {w:S.w,h:S.h,f35:S.persp.f35,Lmm:model.alto,A:m.A,B:m.B,floorP:S.floor,
    refFoot:S.persp.link?S.floor:S.persp.refFoot,link:S.persp.link};
}
function inputsFrom(b,J,fs){
  J=J||(p=>p);
  const floorP=J(b.floorP);
  return {w:b.w,h:b.h,f35:b.f35*fs,Lmm:b.Lmm,A:J(b.A),B:J(b.B),floorP,
    refFoot:b.link?floorP:(b.refFoot?J(b.refFoot):null),l:horizonL(J)};
}
function recompute(crop=true){
  const model=refModel();
  S.m=contourMetrics();
  S.sPlane=(S.m&&model&&S.m.L>0)?model.alto/S.m.L:null;
  S.pm=null;
  const b=baseInputs();
  if(b) S.pm=Geo.solve(inputsFrom(b,null,1));
  if(crop) buildCrop();
}

/* ======================= medidas ======================= */
function measureAt(p){
  const r={plano:null,persp:null};
  if(S.sPlane&&S.floor) r.plano=(S.floor.y-p.y)*S.sPlane;
  if(S.pm){const h=Geo.heightAt(S.pm,p);if(h!=null&&isFinite(h)) r.persp=h;}
  return r;
}
/* Incertidumbre por Monte Carlo (semilla fija: resultado reproducible). */
function mcSigma(p,N=250){
  const b=baseInputs(); if(!b) return null;
  const r=rng(20260101),sg=S.sigma;
  const J=q=>({x:q.x+gauss(r)*sg,y:q.y+gauss(r)*sg});
  const a=[],c=[];
  for(let i=0;i<N;i++){
    const inp=inputsFrom(b,J,1+0.03*gauss(r)),pj=J(p);
    const Lpx=Math.hypot(inp.A.x-inp.B.x,inp.A.y-inp.B.y);
    if(Lpx>1e-6) a.push((inp.floorP.y-pj.y)*inp.Lmm/Lpx);
    const sol=Geo.solve(inp);
    if(sol){const h=Geo.heightAt(sol,pj);if(h!=null&&isFinite(h)) c.push(h);}
  }
  return {plano:stdev(a),persp:c.length>N*0.6?stdev(c):null};
}

/* ======================= escala del plano para herramientas manuales ======================= */
function manualScale(){
  if(!S.sPlane) return null;
  if(S.man.plane==='sub'&&S.pm){
    const zr=S.pm.plR.G[2],zs=S.pm.plS.G[2];
    if(zr>0&&zs>0) return S.sPlane*(zs/zr);
  }
  return S.sPlane;
}

/* ======================= interfaz: carga de modelos ======================= */
function fillModels(){
  const only3=$('only3').checked,sel=$('model'),cur=S.modelId;
  sel.innerHTML='<option value="">— seleccionar modelo —</option>';
  const years=[...new Set(S.models.map(m=>m.anio))].sort((a,b)=>b-a);
  for(const y of years){
    const list=S.models.filter(m=>m.anio===y&&(!only3||m.camaras===3||m.id===cur));
    if(!list.length) continue;
    const og=document.createElement('optgroup');og.label=String(y);
    list.slice().reverse().forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.nombre+'  ·  '+m.alto.toFixed(1)+' mm';og.appendChild(o);});
    sel.appendChild(og);
  }
  sel.value=cur;
}
function fillCopyModels(){
  const sel=$('copyModel');
  sel.innerHTML='<option value="">Mismo que la referencia</option>';
  const years=[...new Set(S.models.map(m=>m.anio))].sort((a,b)=>b-a);
  for(const y of years){
    const og=document.createElement('optgroup');og.label=String(y);
    S.models.filter(m=>m.anio===y).reverse().forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.nombre+'  ·  '+m.alto.toFixed(1)+' mm';og.appendChild(o);});
    sel.appendChild(og);
  }
}
async function cargarModelos(){
  const r=await fetch('/api/modelos');const j=await r.json();
  S.models=j.modelos;S.fuente=j.fuente;
  $('srcNote').textContent='Dimensiones: '+j.fuente;
  fillModels();fillCopyModels();
}

/* ======================= carga de la fotografía ======================= */
function showErr(t){$('err').textContent=t||'';}
async function subir(file){
  if(!file) return;
  showErr('');
  let j;
  try{
    const r=await fetch('/api/foto',{method:'POST',headers:{'Content-Type':file.type||'application/octet-stream','X-Nombre':encodeURIComponent(file.name)},body:file});
    if(!r.ok) throw new Error(await r.text()||('HTTP '+r.status));
    j=await r.json();
  }catch(e){showErr(String(e.message||e));return;}
  const img=new Image();
  img.onload=()=>{
    resetAll();
    S.img=img;S.w=img.naturalWidth;S.h=img.naturalHeight;S.photo=j.id;S.exif=j.exif||{};S.name=j.nombre;
    const f=S.exif.focal_35mm;
    if(f){S.persp.f35=f;S.persp.f35src='EXIF (focal equivalente 35 mm)';}
    else{S.persp.f35=26;S.persp.f35src='valor por defecto: sin EXIF; iPhone, cámara principal ≈ 24–26 mm';}
    $('f35').value=S.persp.f35;
    $('drop').style.display='none';
    fit();setTool('contour');recompute();ui();draw();
  };
  img.onerror=()=>showErr('El navegador no pudo decodificar la imagen.');
  img.src='/api/foto/'+j.id;
}
function resetAll(){
  S.contour={pts:[],closed:false};S.floor=null;
  Object.assign(S.persp,{h1:null,h2:null,vl:[],refFoot:null,link:false});$('link').checked=false;
  S.ground=[];S.gdraft=null;S.pins=[];S.draft=null;
  S.man.rulers=[];S.man.curves=[];S.man.copies=[];S.man.sel=null;
  S.m=null;S.sPlane=null;S.pm=null;S.crop=null;S.viewSet=false;
}

/* ======================= vista ======================= */
function resize(){
  const r=$('stage').getBoundingClientRect();
  DPR=window.devicePixelRatio||1;
  cv.width=Math.max(1,Math.round(r.width*DPR));cv.height=Math.max(1,Math.round(r.height*DPR));
  cv.style.width=r.width+'px';cv.style.height=r.height+'px';
  if(S.img&&!S.viewSet) fit();
  draw();
}
function fit(){
  const r=$('stage').getBoundingClientRect();
  const aw=r.width-G-24,ah=r.height-24;
  if(!S.img||aw<=0||ah<=0) return;
  const k=Math.min(aw/S.w,ah/S.h);
  S.view.k=k;S.view.tx=G+12+(aw-S.w*k)/2;S.view.ty=12+(ah-S.h*k)/2;
}
function zoomAt(sp,f){
  const ip=s2i(sp),k=clamp(S.view.k*f,0.02,80);
  S.view.k=k;S.view.tx=sp.x-ip.x*k;S.view.ty=sp.y-ip.y*k;S.viewSet=true;draw();
}

/* ======================= herramientas ======================= */
const HINTS={
  contour:'<b>CONTORNO</b> · Clic en el borde del iPhone para fijar vértices. Cierra sobre el primer punto o con Intro. Rueda: zoom · botón derecho o Espacio+arrastrar: desplazar.',
  floor:'<b>SUELO</b> · Marca el punto de contacto de los pies con el suelo.',
  measure:'<b>MEDIR</b> · El punto sigue al ratón; la altura se lee en la cabecera. Clic: fijar la medida en la tabla.',
  horizon:'<b>HORIZONTE</b> · ',
  refFoot:'<b>BASE DEL iPHONE</b> · Clic en el suelo, justo bajo el teléfono (donde caería una plomada).',
  ground:'<b>SUELO</b> · Clic en un punto del suelo y después en otro (puede ser hacia el horizonte) para obtener la distancia real.',
  ruler:'<b>REGLA</b> · Dos clics. Longitud en el plano de la escala elegida.',
  curve:'<b>CURVA</b> · Clics sucesivos; Intro o doble clic para terminar. Se reparte el iPhone a lo largo del arco.',
  copy:'<b>COPIAS</b> · Clic: colocar un iPhone. Arrastra para mover; Q/E giran; Supr elimina.',
  none:''
};
function hintText(){
  if(!S.img) return 'Carga una fotografía para comenzar.';
  if(S.tool==='horizon'){
    const m=S.persp.horMode;
    const t=m==='level'?'Clic sobre la línea del horizonte (se supone horizontal en la imagen).':m==='free'?'Dos clics sobre la línea del horizonte.':'Cuatro líneas: dos pares de rectas paralelas del suelo (p. ej. aristas de baldosas). Cada línea son 2 clics.';
    return HINTS.horizon+t;
  }
  return HINTS[S.tool]||'';
}
function setTool(t){
  S.tool=t;S.draft=null;S.gdraft=null;
  setCursor();ui();draw();
}
function setCursor(){cv.style.cursor=S.panning?'grabbing':(S.tool==='measure'?'none':'crosshair');}
function closeContour(){
  if(S.contour.pts.length<3) return;
  S.contour.closed=true;recompute();autoAdvance();ui();draw();
}
function autoAdvance(){
  if(!S.contour.closed) return setTool('contour');
  if(!S.modelId) return;
  if(!S.floor) return setTool('floor');
  if(S.mode==='persp'){
    if(!horizonL(null)) return setTool('horizon');
    if(!S.persp.link&&!S.persp.refFoot) return setTool('refFoot');
  }
  setTool(S.mode==='manual'?'ruler':'measure');
}
function clickHorizon(ip){
  const P=S.persp,q={x:ip.x,y:ip.y};
  if(P.horMode==='level'){P.h1=q;recompute();autoAdvance();}
  else if(P.horMode==='free'){
    if(!S.draft||S.draft.type!=='hor') S.draft={type:'hor',pts:[q]};
    else{P.h1=S.draft.pts[0];P.h2=q;S.draft=null;recompute();autoAdvance();}
  }else{
    if(!S.draft||S.draft.type!=='vl'){ if(P.vl.length>=4) P.vl=[]; S.draft={type:'vl',pts:[q]}; }
    else{P.vl.push({a:S.draft.pts[0],b:q});S.draft=null;if(P.vl.length>=4){recompute();autoAdvance();}}
  }
}
function toolClick(ip){
  const t=S.tool,q={x:ip.x,y:ip.y};
  if(t==='contour'){ if(S.contour.closed) return; S.contour.pts.push(q); recompute(false); }
  else if(t==='floor'){ S.floor=q; recompute(); autoAdvance(); }
  else if(t==='measure'){ S.pins.push(q); }
  else if(t==='horizon'){ clickHorizon(ip); }
  else if(t==='refFoot'){ S.persp.refFoot=q;S.persp.link=false;$('link').checked=false;recompute();autoAdvance(); }
  else if(t==='ground'){ if(!S.gdraft) S.gdraft=q; else{S.ground.push({a:S.gdraft,b:q});S.gdraft=null;} }
  else if(t==='ruler'){ if(!S.draft||S.draft.type!=='ruler') S.draft={type:'ruler',pts:[q]}; else{S.man.rulers.push({a:S.draft.pts[0],b:q});S.draft=null;} }
  else if(t==='curve'){ if(!S.draft||S.draft.type!=='curve') S.draft={type:'curve',pts:[]}; S.draft.pts.push(q); }
  else if(t==='copy'){
    if(!S.crop) return;
    const c={x:q.x,y:q.y,ang:0,modelId:S.man.copyModel};
    S.man.copies.push(c);S.man.sel=c;
  }
  ui();draw();
}
function finishCurve(){
  if(S.draft&&S.draft.type==='curve'&&S.draft.pts.length>=2){S.man.curves.push({pts:S.draft.pts});}
  S.draft=null;ui();draw();
}

/* ======================= manejadores (arrastre de puntos) ======================= */
function handles(){
  const H=[],add=(p,kind)=>{if(p)H.push({p,kind});};
  S.contour.pts.forEach(p=>add(p,'contour'));
  add(S.floor,'floor');
  if(S.mode==='persp'){
    const P=S.persp;
    if(P.horMode==='level') add(P.h1,'hor');
    else if(P.horMode==='free'){add(P.h1,'hor');add(P.h2,'hor');}
    else P.vl.forEach(l=>{add(l.a,'vl');add(l.b,'vl');});
    if(!P.link) add(P.refFoot,'foot');
    S.ground.forEach(g=>{add(g.a,'g');add(g.b,'g');});
  }
  if(S.mode==='manual'){
    S.man.rulers.forEach(r=>{add(r.a,'man');add(r.b,'man');});
    S.man.curves.forEach(c=>c.pts.forEach(p=>add(p,'man')));
    S.man.copies.forEach(c=>add(c,'copy'));
  }
  S.pins.forEach(p=>add(p,'pin'));
  return H;
}
function hitHandle(sp){
  const H=handles();let best=null,bd=10;
  for(const h of H){const d=dist(sp,i2s(h.p));if(d<bd){bd=d;best=h;}}
  return best;
}
function copyDims(c){
  if(!S.crop||!S.m) return null;
  const mdl=modelById(c.modelId)||refModel(); if(!mdl) return null;
  const sc=manualScale(); if(!sc) return null;
  const Lpx=mdl.alto/sc;                         /* longitud en px de imagen */
  const f=Lpx/S.m.L;                             /* factor sobre el recorte nativo */
  return {f,w:S.crop.cw/S.crop.sc*f,h:S.crop.ch/S.crop.sc*f};
}
function hitCopy(sp){
  if(S.tool!=='copy') return null;
  const ip=s2i(sp);
  for(let i=S.man.copies.length-1;i>=0;i--){
    const c=S.man.copies[i],d=copyDims(c); if(!d) continue;
    const a=-c.ang*Math.PI/180,dx=ip.x-c.x,dy=ip.y-c.y;
    const u=dx*Math.cos(a)-dy*Math.sin(a),v=dx*Math.sin(a)+dy*Math.cos(a);
    if(Math.abs(u)<=d.w/2&&Math.abs(v)<=d.h/2) return c;
  }
  return null;
}

/* ======================= eventos del lienzo ======================= */
let drag=null,pan=null;
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('pointerdown',e=>{
  if(!S.img) return;
  const sp=evPos(e);
  if(e.button===1||e.button===2||(e.button===0&&S.space)){
    pan={x:sp.x,y:sp.y,tx:S.view.tx,ty:S.view.ty};S.panning=true;cv.setPointerCapture(e.pointerId);setCursor();return;
  }
  if(e.button!==0||sp.x<G) return;
  const ip=s2i(sp);
  if(S.tool==='contour'&&!S.contour.closed&&S.contour.pts.length>=3&&dist(sp,i2s(S.contour.pts[0]))<10){closeContour();return;}
  if(S.mode==='manual'){
    const c=hitCopy(sp);
    if(c){S.man.sel=c;drag={p:c,kind:'copy'};cv.setPointerCapture(e.pointerId);ui();draw();return;}
  }
  const hit=hitHandle(sp);
  if(hit){drag=hit;if(hit.kind==='copy')S.man.sel=hit.p;cv.setPointerCapture(e.pointerId);return;}
  toolClick(ip);
});
cv.addEventListener('pointermove',e=>{
  const sp=evPos(e);S.mouse=sp;
  if(pan){S.view.tx=pan.tx+(sp.x-pan.x);S.view.ty=pan.ty+(sp.y-pan.y);S.viewSet=true;draw();return;}
  if(drag){
    const ip=s2i(sp);drag.p.x=ip.x;drag.p.y=ip.y;
    if(drag.kind==='contour') S.cropDirty=true;
    recompute(false);ui();draw();return;
  }
  updateLive();draw();
});
cv.addEventListener('pointerup',()=>{
  if(pan){pan=null;S.panning=false;setCursor();}
  if(drag){drag=null;if(S.cropDirty){S.cropDirty=false;recompute(true);}ui();draw();}
});
cv.addEventListener('pointerleave',()=>{S.mouse=null;updateLive();draw();});
cv.addEventListener('dblclick',()=>{
  if(S.tool==='curve'&&S.draft&&S.draft.type==='curve'){
    const p=S.draft.pts;
    if(p.length>=2&&dist(p[p.length-1],p[p.length-2])<1e-6) p.pop();
    finishCurve();
  }
});
cv.addEventListener('wheel',e=>{e.preventDefault();zoomAt(evPos(e),Math.exp(-e.deltaY*0.0015));},{passive:false});

window.addEventListener('keydown',e=>{
  const tag=(e.target.tagName||'').toLowerCase();
  if(tag==='input'||tag==='select'||tag==='textarea') return;
  if(e.code==='Space'){S.space=true;e.preventDefault();return;}
  if(e.key==='Enter'){
    if(S.tool==='contour'&&!S.contour.closed) closeContour();
    else if(S.tool==='curve') finishCurve();
  }else if(e.key==='Escape'){S.draft=null;S.gdraft=null;ui();draw();}
  else if(e.key==='Backspace'||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z')){e.preventDefault();undo();}
  else if(e.key==='Delete'){
    const c=S.man.sel;if(c){S.man.copies=S.man.copies.filter(x=>x!==c);S.man.sel=null;ui();draw();}
  }else if(e.key.toLowerCase()==='q'||e.key.toLowerCase()==='e'){
    const c=S.man.sel;if(c){c.ang+=(e.key.toLowerCase()==='e'?1:-1)*(e.shiftKey?15:1);draw();}
  }
});
window.addEventListener('keyup',e=>{if(e.code==='Space')S.space=false;});

function undo(){
  if(S.draft&&S.draft.pts.length){S.draft.pts.pop();if(!S.draft.pts.length)S.draft=null;}
  else if(S.tool==='contour'||(!S.contour.closed&&S.contour.pts.length)){
    if(S.contour.closed){S.contour.closed=false;S.m=null;S.crop=null;S.sPlane=null;S.pm=null;}
    else S.contour.pts.pop();
    recompute(false);
  }
  ui();draw();
}

/* ======================= lectura en vivo ======================= */
function liveValues(){
  if(!(S.mouse&&S.img&&S.mouse.x>G)) return null;
  return measureAt(s2i(S.mouse));
}
function updateLive(){
  const r=liveValues(),model=refModel();
  const act=r?(S.mode==='persp'?r.persp:r.plano):null;
  $('roVal').textContent=act==null?'—':fmt(act/10,1)+' cm';
  let sub='';
  if(act!=null&&model) sub='= '+fmt(act/model.alto,2)+' iPhone';
  if(S.mode==='persp'&&S.pm) sub+=(sub?'  ·  ':'')+'cámara a '+fmt(S.pm.Hc/1000,2)+' m';
  $('roSub').textContent=sub;
  $('lvPlano').textContent=r&&r.plano!=null?fmtLen(r.plano):'—';
  $('lvPersp').textContent=r&&r.persp!=null?fmtLen(r.persp):'—';
  $('lvDiff').textContent=r&&r.plano!=null&&r.persp!=null?fmt((r.persp-r.plano)/10,1)+' cm  ('+fmt(100*(r.persp-r.plano)/r.persp,1)+' %)':'—';
  $('lvUnits').textContent=act!=null&&model?fmt(act/model.alto,2)+' × '+model.nombre:'—';
}

/* ======================= panel ======================= */
function ui(){
  const model=refModel(),m=S.m;
  document.querySelectorAll('[data-tool]').forEach(b=>b.classList.toggle('on',b.dataset.tool===S.tool));
  document.querySelectorAll('#modes button').forEach(b=>b.classList.toggle('on',b.dataset.mode===S.mode));
  $('secPersp').style.display=S.mode==='persp'?'':'none';
  $('secMan').style.display=S.mode==='manual'?'':'none';
  $('hint').innerHTML=hintText();$('hint').style.display=hintText()?'':'none';
  $('kName').textContent=S.name||'—';
  $('kRes').textContent=S.img?S.w+' × '+S.h+' px':'—';
  const ex=S.exif;$('kCam').textContent=(ex&&(ex.marca||ex.modelo))?[ex.marca,ex.modelo].filter(Boolean).join(' '):'—';
  $('kNom').textContent=model?model.alto.toFixed(1)+' × '+model.ancho.toFixed(1)+' × '+model.grosor+' mm':'—';
  $('kL').textContent=m?fmt(m.L,1)+' px':'—';
  $('kW').textContent=m?fmt(m.W,1)+' px':'—';
  const asp=$('kAsp'),tilt=$('kTilt');asp.className='';tilt.className='';
  if(m&&model){
    const dv=(m.W/m.L)/(model.ancho/model.alto)-1;
    asp.textContent=fmt(m.W/m.L,3)+' / '+fmt(model.ancho/model.alto,3)+'  ('+(dv>=0?'+':'')+fmt(dv*100,1)+' %)';
    asp.className=Math.abs(dv)>0.06?'warn':'ok';
    tilt.textContent=fmt(Math.abs(m.tilt),1)+'°';tilt.className=Math.abs(m.tilt)>8?'warn':'ok';
  }else{asp.textContent='—';tilt.textContent='—';}
  $('kScale').textContent=S.sPlane?fmt(S.sPlane,4)+' mm/px':'—';
  $('kFloor').textContent=S.floor?fmt(S.floor.x,0)+', '+fmt(S.floor.y,0):'—';
  $('f35note').textContent='Fuente: '+S.persp.f35src+'.';
  $('rowHorY').style.display=S.persp.horMode==='level'?'':'none';
  if(S.persp.horMode==='level'&&document.activeElement!==$('horY')) $('horY').value=S.persp.h1?Math.round(S.persp.h1.y):'';
  /* perspectiva */
  const pm=S.pm;
  const setK=(id,t,cls)=>{const e=$(id);e.textContent=t;e.className=cls||'';};
  if(pm){
    const hc=pm.Hc/1000;
    setK('kPitch',fmt(Geo.pitchDeg(pm.cam),1)+'° ('+(Geo.pitchDeg(pm.cam)>=0?'hacia arriba':'hacia abajo')+')');
    setK('kHc',fmt(hc,2)+' m',(hc<0.3||hc>3.5)?'warn':'ok');
    setK('kDr',fmt(pm.plR.dh*pm.Hc/1000,2)+' m');
    setK('kDs',fmt(pm.plS.dh*pm.Hc/1000,2)+' m');
    setK('kRatio','× '+fmt(pm.plS.G[2]/pm.plR.G[2],2));
  }else{['kPitch','kHc','kDr','kDs','kRatio'].forEach(id=>setK(id,'—'));}
  /* suelo: pares */
  const gl=$('gList');gl.innerHTML='';
  S.ground.forEach((g,i)=>{
    const d=groundPair(g);
    const row=document.createElement('div');
    row.innerHTML='<span>D'+(i+1)+(d?' · '+fmt(d.dist/1000,2)+' m':' · sin calibrar')+'</span><span>'+(d?'A '+fmt(d.ra/1000,1)+' m · B '+fmt(d.rb/1000,1)+' m':'')+'</span>';
    const x=document.createElement('button');x.textContent='×';x.onclick=()=>{S.ground.splice(i,1);ui();draw();};
    row.appendChild(x);gl.appendChild(row);
  });
  /* manual */
  const ml=$('mList');ml.innerHTML='';const sc=manualScale();
  S.man.rulers.forEach((r,i)=>{
    const row=document.createElement('div');row.innerHTML='<span>Regla '+(i+1)+'</span><span>'+(sc?fmtLen(dist(r.a,r.b)*sc):'—')+'</span>';
    const x=document.createElement('button');x.textContent='×';x.onclick=()=>{S.man.rulers.splice(i,1);ui();draw();};row.appendChild(x);ml.appendChild(row);
  });
  S.man.curves.forEach((c,i)=>{
    const pl=polyline(c.pts),L=pl.total;
    const row=document.createElement('div');
    row.innerHTML='<span>Curva '+(i+1)+'</span><span>'+(sc&&model?fmtLen(L*sc)+' · '+fmt(L*sc/model.alto,2)+' iPhone':'—')+'</span>';
    const x=document.createElement('button');x.textContent='×';x.onclick=()=>{S.man.curves.splice(i,1);ui();draw();};row.appendChild(x);ml.appendChild(row);
  });
  if(S.man.copies.length){const row=document.createElement('div');row.innerHTML='<span>Copias de iPhone</span><span>'+S.man.copies.length+'</span>';ml.appendChild(row);}
  /* medidas fijadas */
  const t=$('pinTable');
  let html='<tr><th>#</th><th>PLANO ÚNICO</th><th>PERSPECTIVA</th><th></th></tr>';
  S.pins.forEach((p,i)=>{
    const r=measureAt(p),u=(r.plano!=null||r.persp!=null)?mcSigma(p):null;
    const f=(v,s)=>v==null?'—':fmt(v/10,1)+(s!=null?' ± '+fmt(s/10,1):'');
    html+='<tr><td>'+(i+1)+'</td><td>'+f(r.plano,u&&u.plano)+'</td><td>'+f(r.persp,u&&u.persp)+'</td><td><button data-pin="'+i+'">×</button></td></tr>';
  });
  t.innerHTML=html;
  t.querySelectorAll('button[data-pin]').forEach(b=>b.onclick=()=>{S.pins.splice(+b.dataset.pin,1);ui();draw();});
  updateLive();
}
function groundPair(g){
  if(!S.pm) return null;
  const A=Geo.groundMM(S.pm,g.a),B=Geo.groundMM(S.pm,g.b); if(!A||!B) return null;
  const u=S.pm.cam.u,hr=P=>Geo.len(Geo.add(P,Geo.mul(u,S.pm.Hc)));
  return {dist:Geo.len(Geo.sub(A,B)),ra:hr(A),rb:hr(B)};
}

/* ======================= geometría de curvas ======================= */
function splinePts(pts){
  if(pts.length<3||!S.man.smooth) return pts.slice();
  const out=[],n=pts.length;
  for(let i=0;i<n-1;i++){
    const p0=pts[Math.max(i-1,0)],p1=pts[i],p2=pts[i+1],p3=pts[Math.min(i+2,n-1)];
    for(let k=0;k<20;k++){
      const t=k/20,t2=t*t,t3=t2*t;
      out.push({
        x:0.5*(2*p1.x+(-p0.x+p2.x)*t+(2*p0.x-5*p1.x+4*p2.x-p3.x)*t2+(-p0.x+3*p1.x-3*p2.x+p3.x)*t3),
        y:0.5*(2*p1.y+(-p0.y+p2.y)*t+(2*p0.y-5*p1.y+4*p2.y-p3.y)*t2+(-p0.y+3*p1.y-3*p2.y+p3.y)*t3)});
    }
  }
  out.push(pts[n-1]);return out;
}
function polyline(pts){
  const s=splinePts(pts),cum=[0];
  for(let i=1;i<s.length;i++) cum.push(cum[i-1]+dist(s[i],s[i-1]));
  return {s,cum,total:cum[cum.length-1]||0};
}
function atLen(pl,d){
  const {s,cum}=pl;
  if(d<=0){const t=norm2(s[1].x-s[0].x,s[1].y-s[0].y);return {x:s[0].x,y:s[0].y,tx:t[0],ty:t[1]};}
  for(let i=1;i<s.length;i++){
    if(cum[i]>=d){
      const seg=cum[i]-cum[i-1]||1,f=(d-cum[i-1])/seg,t=norm2(s[i].x-s[i-1].x,s[i].y-s[i-1].y);
      return {x:s[i-1].x+(s[i].x-s[i-1].x)*f,y:s[i-1].y+(s[i].y-s[i-1].y)*f,tx:t[0],ty:t[1]};
    }
  }
  const n=s.length,t=norm2(s[n-1].x-s[n-2].x,s[n-1].y-s[n-2].y);return {x:s[n-1].x,y:s[n-1].y,tx:t[0],ty:t[1]};
}
function norm2(x,y){const n=Math.hypot(x,y)||1;return [x/n,y/n];}

/* ======================= dibujo ======================= */
function txt(t,x,y,col,align,font){
  ctx.font=font||('10px '+MONO);ctx.textAlign=align||'left';ctx.textBaseline='alphabetic';
  ctx.lineWidth=3;ctx.strokeStyle='rgba(6,8,10,.9)';ctx.strokeText(t,x,y);
  ctx.fillStyle=col||C.txt;ctx.fillText(t,x,y);
}
function seg(a,b,col,w,dash){
  ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
  ctx.lineWidth=w||1;ctx.strokeStyle=col;ctx.setLineDash(dash||[]);ctx.stroke();ctx.setLineDash([]);
}
function pinGlyph(p,col,r,big){
  r=r||4.5;
  ctx.beginPath();ctx.arc(p.x,p.y,big?r+3:r,0,6.2832);ctx.fillStyle=C.bg;ctx.fill();ctx.lineWidth=1.5;ctx.strokeStyle=col;ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(p.x-r-4,p.y);ctx.lineTo(p.x-r+1,p.y);ctx.moveTo(p.x+r-1,p.y);ctx.lineTo(p.x+r+4,p.y);
  ctx.moveTo(p.x,p.y-r-4);ctx.lineTo(p.x,p.y-r+1);ctx.moveTo(p.x,p.y+r-1);ctx.lineTo(p.x,p.y+r+4);
  ctx.lineWidth=1;ctx.stroke();
  ctx.beginPath();ctx.arc(p.x,p.y,1.3,0,6.2832);ctx.fillStyle=col;ctx.fill();
}
function viewBounds(){
  const W=cv.width/DPR,H=cv.height/DPR;
  return {W,H,p0:s2i({x:G,y:0}),p1:s2i({x:W,y:H})};
}
function imgLine(l,col,w,dash){
  const {p0,p1}=viewBounds();let A,B;
  if(Math.abs(l[1])>=Math.abs(l[0])){A={x:p0.x,y:-(l[0]*p0.x+l[2])/l[1]};B={x:p1.x,y:-(l[0]*p1.x+l[2])/l[1]};}
  else{A={x:-(l[1]*p0.y+l[2])/l[0],y:p0.y};B={x:-(l[1]*p1.y+l[2])/l[0],y:p1.y};}
  seg(i2s(A),i2s(B),col,w,dash);
}
function drawCropAt(sp,angDeg,pxPerCropPx,alpha){
  if(!S.crop) return;
  ctx.save();ctx.globalAlpha=alpha==null?1:alpha;
  ctx.translate(sp.x,sp.y);ctx.rotate(angDeg*Math.PI/180);ctx.scale(pxPerCropPx,pxPerCropPx);
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(S.crop.cv,-S.crop.cw/2,-S.crop.ch/2);
  ctx.restore();
}

function ladder(){
  const model=refModel();
  if(!model||!S.floor||!S.m) return null;
  const persp=S.mode==='persp'&&S.pm;
  const yAt=persp
    ?(hmm)=>{const Zu=hmm/S.pm.Hc,P=Geo.add(S.pm.plS.G,Geo.mul(S.pm.cam.u,Zu));return P[2]>1e-6?Geo.project(S.pm.cam,P):null;}
    :(hmm)=>({x:S.floor.x,y:S.floor.y-hmm/S.sPlane});
  const st=[];
  for(let k=0;k<400;k++){
    const b=yAt(k*model.alto),t=yAt((k+1)*model.alto);
    if(!b||!t) break;
    st.push({k,yb:b.y,yt:t.y,hb:k*model.alto,ht:(k+1)*model.alto});
    if(Math.min(b.y,t.y)<-S.h*0.15) break;
  }
  return st;
}

function drawGuides(st){
  if(!st) return;
  const v=S.view;
  ctx.save();ctx.beginPath();ctx.rect(G,0,cv.width/DPR-G,cv.height/DPR);ctx.clip();
  st.forEach(s=>{
    const y=s.yt*v.k+v.ty;
    ctx.beginPath();ctx.moveTo(G,y);ctx.lineTo(cv.width/DPR,y);ctx.lineWidth=1;ctx.strokeStyle='rgba(224,165,38,.13)';ctx.stroke();
  });
  ctx.restore();
}

function drawGutter(st){
  const W=cv.width/DPR,H=cv.height/DPR,v=S.view,model=refModel();
  ctx.save();
  ctx.fillStyle=C.panel;ctx.fillRect(0,0,G,H);
  ctx.strokeStyle=C.line2;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(G+.5,0);ctx.lineTo(G+.5,H);ctx.stroke();
  ctx.beginPath();ctx.rect(0,0,G,H);ctx.clip();
  txt('ESCALA iPHONE',10,16,C.mut,'left','600 9px '+MONO);
  if(!st){
    txt('SIN CALIBRAR',10,34,C.warn,'left','9px '+MONO);
    txt(!S.modelId?'modelo':(!S.contour.closed?'contorno':'suelo'),10,46,C.mut,'left','9px '+MONO);
    ctx.restore();return;
  }
  txt(model.nombre,10,28,C.ref,'left','9px '+MONO);
  st.forEach(s=>{
    const yb=s.yb*v.k+v.ty,yt=s.yt*v.k+v.ty,hb=yb-yt;
    if((yb<0&&yt<0)||(yb>H&&yt>H)||hb<2) return;
    const x0=12,x1=G-14;
    ctx.fillStyle=s.k%2?'rgba(94,194,183,.05)':'rgba(94,194,183,.10)';ctx.fillRect(x0,yt,x1-x0,hb);
    if(S.crop&&hb>14){
      const sc=Math.min((x1-x0-6)/S.crop.cw,(hb-4)/S.crop.ch);
      ctx.save();ctx.translate((x0+x1)/2,(yt+yb)/2);ctx.scale(sc,sc);ctx.imageSmoothingEnabled=true;
      ctx.drawImage(S.crop.cv,-S.crop.cw/2,-S.crop.ch/2);ctx.restore();
    }
    ctx.strokeStyle=C.ref;ctx.lineWidth=1;ctx.strokeRect(x0+.5,yt+.5,x1-x0,hb);
    if(hb>12){
      txt(fmt(s.ht/10,1),G-4,yt+10,C.acc,'right','9px '+MONO);
    }
  });
  ctx.restore();
}

function drawContour(){
  const P=S.contour.pts;if(!P.length) return;
  const sp=P.map(i2s);
  ctx.beginPath();sp.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));
  if(S.contour.closed){ctx.closePath();ctx.fillStyle='rgba(94,194,183,.14)';ctx.fill();}
  ctx.lineWidth=1.5;ctx.strokeStyle=C.ref;ctx.stroke();
  if(!S.contour.closed&&S.tool==='contour'&&S.mouse&&S.mouse.x>G){
    seg(sp[sp.length-1],S.mouse,C.ref,1,[4,3]);
    if(P.length>=3&&dist(S.mouse,sp[0])<10) pinGlyph(sp[0],C.acc,5,true);
  }
  const m=S.m;
  if(m){
    const ex=(a,e)=>i2s({x:m.cx+m.ax*a+m.ex*e,y:m.cy+m.ay*a+m.ey*e});
    const c=[ex(m.amax,m.emin),ex(m.amax,m.emax),ex(m.amin,m.emax),ex(m.amin,m.emin)];
    ctx.beginPath();c.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();
    ctx.setLineDash([4,4]);ctx.lineWidth=1;ctx.strokeStyle='rgba(94,194,183,.55)';ctx.stroke();ctx.setLineDash([]);
    const a=i2s(m.A),b=i2s(m.B);
    seg(a,b,C.acc,1,[2,3]);
    const nx=-(b.y-a.y),ny=b.x-a.x,nn=Math.hypot(nx,ny)||1;
    [a,b].forEach(p=>seg({x:p.x-nx/nn*8,y:p.y-ny/nn*8},{x:p.x+nx/nn*8,y:p.y+ny/nn*8},C.acc,1.5));
    const mid=i2s({x:m.cx,y:m.cy});
    txt('L = '+fmt(m.L,1)+' px',mid.x+14,mid.y,C.acc);
  }
  sp.forEach((p,i)=>pinGlyph(p,i===0&&!S.contour.closed?C.acc:C.ref,4));
}

function drawFloor(){
  if(!S.floor) return;
  const v=S.view,f=i2s(S.floor);
  seg({x:Math.max(G,v.tx),y:f.y},{x:v.tx+S.w*v.k,y:f.y},C.acc,1,[6,4]);
  if(S.mode==='persp'&&S.pm){
    const d=Geo.vdir(S.pm.cam,S.floor);
    seg(f,{x:f.x+d[0]*3000*v.k,y:f.y+d[1]*3000*v.k},'rgba(224,165,38,.35)',1,[3,5]);
  }
  pinGlyph(f,C.acc,4.5);
  txt('SUELO',f.x+10,f.y-8,C.acc);
}

function drawPersp(){
  if(S.mode!=='persp') return;
  const P=S.persp,l=horizonL(null);
  if(l){
    imgLine(l,C.hor,1.2);
    const mid=s2i({x:(G+cv.width/DPR)/2,y:0});
    const y=Math.abs(l[1])>1e-9?-(l[0]*mid.x+l[2])/l[1]:0;
    const sp=i2s({x:mid.x,y});txt('HORIZONTE',sp.x,sp.y-6,C.hor,'center');
  }
  if(P.horMode==='level'&&P.h1) pinGlyph(i2s({x:S.w/2,y:P.h1.y}),C.hor,4);
  else if(P.horMode==='free'){ if(P.h1) pinGlyph(i2s(P.h1),C.hor,4); if(P.h2) pinGlyph(i2s(P.h2),C.hor,4); }
  else if(P.horMode==='vp'){
    P.vl.forEach(L=>{
      const a=i2s(L.a),b=i2s(L.b);
      const lh=Geo.cross([L.a.x,L.a.y,1],[L.b.x,L.b.y,1]);imgLine(lh,'rgba(143,168,255,.28)',1,[5,5]);
      seg(a,b,C.hor,1.5);pinGlyph(a,C.hor,3.5);pinGlyph(b,C.hor,3.5);
    });
    if(S.draft&&S.draft.type==='vl'){const a=i2s(S.draft.pts[0]);pinGlyph(a,C.hor,3.5);if(S.mouse) seg(a,S.mouse,C.hor,1,[4,3]);}
  }
  if(S.draft&&S.draft.type==='hor'){const a=i2s(S.draft.pts[0]);pinGlyph(a,C.hor,4);if(S.mouse) seg(a,S.mouse,C.hor,1,[4,3]);}
  /* base del iPhone */
  const rf=P.link?null:P.refFoot;
  if(rf&&S.m){
    const a=i2s(rf),c=i2s({x:S.m.cx,y:S.m.cy});
    seg(c,a,C.ref,1,[2,4]);pinGlyph(a,C.ref,4.5);txt('BASE iPHONE',a.x+10,a.y+14,C.ref);
  }
  /* distancias en el suelo */
  S.ground.forEach((g,i)=>{
    const a=i2s(g.a),b=i2s(g.b),d=groundPair(g);
    seg(a,b,C.hor,1.5);pinGlyph(a,C.hor,4);pinGlyph(b,C.hor,4);
    txt(d?('D'+(i+1)+' = '+fmt(d.dist/1000,2)+' m'):('D'+(i+1)),(a.x+b.x)/2+8,(a.y+b.y)/2-6,C.hor);
  });
  if(S.gdraft){const a=i2s(S.gdraft);pinGlyph(a,C.hor,4);if(S.mouse) seg(a,S.mouse,C.hor,1,[4,3]);}
}

function drawManual(){
  if(S.mode!=='manual') return;
  const sc=manualScale(),model=refModel();
  S.man.rulers.forEach((r,i)=>{
    const a=i2s(r.a),b=i2s(r.b);seg(a,b,C.acc,1.5);
    const nx=-(b.y-a.y),ny=b.x-a.x,nn=Math.hypot(nx,ny)||1;
    [a,b].forEach(p=>seg({x:p.x-nx/nn*6,y:p.y-ny/nn*6},{x:p.x+nx/nn*6,y:p.y+ny/nn*6},C.acc,1.5));
    pinGlyph(a,C.acc,3.5);pinGlyph(b,C.acc,3.5);
    txt(sc?fmtLen(dist(r.a,r.b)*sc):'—',(a.x+b.x)/2+8,(a.y+b.y)/2-6,C.acc);
  });
  const drawCurve=(pts,draft)=>{
    if(pts.length<1) return;
    const pl=polyline(pts),sp=pl.s.map(i2s);
    ctx.beginPath();sp.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));
    ctx.lineWidth=1.5;ctx.strokeStyle=C.acc;ctx.setLineDash(draft?[5,4]:[]);ctx.stroke();ctx.setLineDash([]);
    if(sc&&model&&S.crop&&pl.total>0&&pts.length>=2){
      const Lu=model.alto/sc,n=Math.ceil(pl.total/Lu-1e-9),f=Lu/S.m.L;
      for(let i=0;i<n;i++){
        const mid=Math.min(pl.total,(i+0.5)*Lu),q=atLen(pl,mid),part=Math.min(1,(pl.total-i*Lu)/Lu);
        drawCropAt(i2s(q),Math.atan2(q.tx,-q.ty)*180/Math.PI,S.view.k*f/S.crop.sc,part<0.999?0.45:0.9);
      }
      const e=i2s(pl.s[pl.s.length-1]);
      txt(fmtLen(pl.total*sc)+' · '+fmt(pl.total*sc/model.alto,2)+' iPhone',e.x+10,e.y-8,C.acc);
    }
    pts.forEach(p=>pinGlyph(i2s(p),C.acc,3.5));
  };
  S.man.curves.forEach(c=>drawCurve(c.pts,false));
  if(S.draft&&S.draft.type==='curve'){
    const pts=S.draft.pts.slice();if(S.mouse&&S.mouse.x>G&&S.tool==='curve') pts.push(s2i(S.mouse));
    drawCurve(pts,true);
  }
  if(S.draft&&S.draft.type==='ruler'){const a=i2s(S.draft.pts[0]);pinGlyph(a,C.acc,3.5);if(S.mouse) seg(a,S.mouse,C.acc,1,[4,3]);}
  S.man.copies.forEach(c=>{
    const d=copyDims(c);if(!d) return;
    const sp=i2s(c);
    drawCropAt(sp,c.ang,S.view.k*d.f/S.crop.sc,0.95);
    ctx.save();ctx.translate(sp.x,sp.y);ctx.rotate(c.ang*Math.PI/180);
    ctx.strokeStyle=c===S.man.sel?C.acc:'rgba(94,194,183,.7)';ctx.lineWidth=c===S.man.sel?1.5:1;
    ctx.strokeRect(-d.w*S.view.k/2,-d.h*S.view.k/2,d.w*S.view.k,d.h*S.view.k);ctx.restore();
    pinGlyph(sp,C.acc,3);
  });
}

function drawPins(){
  S.pins.forEach((p,i)=>{
    const sp=i2s(p),r=measureAt(p),val=S.mode==='persp'?r.persp:r.plano;
    pinGlyph(sp,C.acc,3.5);
    txt('#'+(i+1)+'  '+(val==null?'—':fmt(val/10,1)+' cm'),sp.x+10,sp.y-8,C.acc);
  });
}

function drawMarker(){
  if(S.tool!=='measure'||!S.mouse||!S.img||S.mouse.x<=G||S.panning) return;
  const sp=S.mouse,W=cv.width/DPR;
  seg({x:G,y:sp.y},{x:W,y:sp.y},'rgba(224,165,38,.55)',1,[5,4]);
  ctx.beginPath();ctx.arc(sp.x,sp.y,5,0,6.2832);ctx.lineWidth=1.5;ctx.strokeStyle=C.acc;ctx.stroke();
  ctx.beginPath();ctx.arc(sp.x,sp.y,1.8,0,6.2832);ctx.fillStyle=C.acc;ctx.fill();
  ctx.beginPath();ctx.moveTo(G-2,sp.y);ctx.lineTo(G-12,sp.y-5);ctx.lineTo(G-12,sp.y+5);ctx.closePath();ctx.fillStyle=C.acc;ctx.fill();
  const r=measureAt(s2i(sp)),v=S.mode==='persp'?r.persp:r.plano;
  if(v!=null) txt(fmt(v/10,1)+' cm',sp.x+12,sp.y-8,C.acc,'left','600 12px '+MONO);
}

function drawLoupe(){
  const box=$('loupe');
  const on=S.mouse&&S.img&&S.mouse.x>G&&!S.panning&&S.tool!=='none';
  box.style.display=on?'block':'none';if(!on) return;
  const lp=$('lp'),g=lp.getContext('2d');g.imageSmoothingEnabled=false;
  const z=4,sw=lp.width/z;
  g.fillStyle=C.bg;g.fillRect(0,0,lp.width,lp.height);
  try{g.drawImage(cv,(S.mouse.x-sw/2)*DPR,(S.mouse.y-sw/2)*DPR,sw*DPR,sw*DPR,0,0,lp.width,lp.height);}catch(_){}
  g.strokeStyle='rgba(224,165,38,.8)';g.lineWidth=1;g.beginPath();
  g.moveTo(lp.width/2,0);g.lineTo(lp.width/2,lp.height/2-8);g.moveTo(lp.width/2,lp.height/2+8);g.lineTo(lp.width/2,lp.height);
  g.moveTo(0,lp.height/2);g.lineTo(lp.width/2-8,lp.height/2);g.moveTo(lp.width/2+8,lp.height/2);g.lineTo(lp.width,lp.height/2);g.stroke();
}

function draw(){
  const W=cv.width/DPR,H=cv.height/DPR;
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.clearRect(0,0,W,H);
  if(!S.img){ctx.fillStyle=C.panel;ctx.fillRect(0,0,G,H);ctx.strokeStyle=C.line2;ctx.beginPath();ctx.moveTo(G+.5,0);ctx.lineTo(G+.5,H);ctx.stroke();return;}
  const v=S.view;
  ctx.fillStyle=C.bg;ctx.fillRect(0,0,W,H);
  ctx.imageSmoothingEnabled=v.k<2.5;
  ctx.drawImage(S.img,v.tx,v.ty,S.w*v.k,S.h*v.k);
  ctx.strokeStyle=C.line2;ctx.lineWidth=1;ctx.strokeRect(v.tx+.5,v.ty+.5,S.w*v.k,S.h*v.k);
  const st=ladder();
  drawGuides(st);drawPersp();drawContour();drawFloor();drawManual();drawPins();drawMarker();
  drawGutter(st);drawLoupe();
}

/* ======================= exportación ======================= */
function descargar(nombre,blob){
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=nombre;document.body.appendChild(a);a.click();
  setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},500);
}
function exportJSON(){
  const model=refModel(),m=S.m,pm=S.pm;
  const out={
    herramienta:'Altímetro iPhone',version:'1.0',fecha:new Date().toISOString(),
    imagen:{nombre:S.name,ancho_px:S.w,alto_px:S.h,exif:S.exif},
    referencia:model?{modelo:model.nombre,alto_mm:model.alto,ancho_mm:model.ancho,grosor_mm:model.grosor}:null,
    contorno_px:S.contour.pts,
    metricas_contorno:m?{L_px:m.L,W_px:m.W,inclinacion_deg:m.tilt,escala_mm_por_px:S.sPlane,A:m.A,B:m.B}:null,
    suelo_px:S.floor,
    perspectiva:pm?{
      f35_mm:S.persp.f35,focal_px:pm.cam.f,cabeceo_deg:Geo.pitchDeg(pm.cam),alabeo_deg:Geo.rollDeg(pm.cam),
      altura_camara_mm:pm.Hc,dist_horizontal_iphone_mm:pm.plR.dh*pm.Hc,dist_horizontal_sujeto_mm:pm.plS.dh*pm.Hc,
      modo_horizonte:S.persp.horMode,iphone_mismo_plano:S.persp.link}:null,
    medidas:S.pins.map((p,i)=>{const r=measureAt(p),u=mcSigma(p);return {n:i+1,punto_px:p,plano_unico_mm:r.plano,perspectiva_mm:r.persp,sigma_plano_mm:u&&u.plano,sigma_perspectiva_mm:u&&u.persp};}),
    distancias_suelo:S.ground.map((g,i)=>{const d=groundPair(g);return {n:i+1,a:g.a,b:g.b,distancia_mm:d&&d.dist};}),
    parametros:{sigma_clic_px:S.sigma,montecarlo_n:250,sigma_focal_rel:0.03},
    fuente_dimensiones:S.fuente
  };
  descargar('medicion_altimetro.json',new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));
}
function exportPNG(){cv.toBlob(b=>b&&descargar('medicion_altimetro.png',b),'image/png');}

/* ======================= enlaces de controles ======================= */
document.querySelectorAll('[data-tool]').forEach(b=>b.addEventListener('click',()=>setTool(b.dataset.tool)));
document.querySelectorAll('#modes button').forEach(b=>b.addEventListener('click',()=>{
  S.mode=b.dataset.mode;S.draft=null;S.gdraft=null;
  autoAdvance();
  if(S.tool==='contour'&&S.contour.closed) setTool('measure');
  ui();draw();
}));
$('bFile').onclick=()=>$('file').click();
$('file').onchange=e=>{subir(e.target.files[0]);e.target.value='';};
$('model').onchange=e=>{S.modelId=e.target.value;recompute();fillModels();autoAdvance();ui();draw();};
$('only3').onchange=fillModels;
$('bUndo').onclick=undo;
$('bClearC').onclick=()=>{S.contour={pts:[],closed:false};S.crop=null;recompute();setTool('contour');};
$('f35').onchange=e=>{const v=parseFloat(e.target.value);if(v>=8&&v<=400){S.persp.f35=v;S.persp.f35src='introducido manualmente';recompute(false);ui();draw();}};
$('horMode').onchange=e=>{const P=S.persp;P.horMode=e.target.value;P.h1=null;P.h2=null;P.vl=[];S.draft=null;recompute(false);setTool('horizon');};
$('horY').onchange=e=>{const v=parseFloat(e.target.value);if(isFinite(v)){S.persp.h1={x:S.w/2,y:v};recompute(false);ui();draw();}};
$('link').onchange=e=>{S.persp.link=e.target.checked;recompute(false);autoAdvance();ui();draw();};
$('bClearG').onclick=()=>{S.ground=[];S.gdraft=null;ui();draw();};
$('smooth').onchange=e=>{S.man.smooth=e.target.checked;ui();draw();};
$('manPlane').onchange=e=>{S.man.plane=e.target.value;ui();draw();};
$('copyModel').onchange=e=>{S.man.copyModel=e.target.value;if(S.man.sel)S.man.sel.modelId=e.target.value;draw();};
$('bClearM').onclick=()=>{S.man.rulers=[];S.man.curves=[];S.man.copies=[];S.man.sel=null;S.draft=null;ui();draw();};
$('bClearP').onclick=()=>{S.pins=[];ui();draw();};
$('sigma').onchange=e=>{const v=parseFloat(e.target.value);if(v>0){S.sigma=v;ui();}};
$('bJson').onclick=exportJSON;
$('bPng').onclick=exportPNG;

const stage=$('stage');
['dragenter','dragover'].forEach(t=>stage.addEventListener(t,e=>{e.preventDefault();$('drop').classList.add('over');}));
['dragleave','drop'].forEach(t=>stage.addEventListener(t,e=>{e.preventDefault();$('drop').classList.remove('over');}));
stage.addEventListener('drop',e=>{const f=e.dataTransfer&&e.dataTransfer.files[0];if(f) subir(f);});
window.addEventListener('resize',resize);
if(window.ResizeObserver) new ResizeObserver(resize).observe(stage);

cargarModelos().then(()=>{resize();ui();});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
