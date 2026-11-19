#!/usr/bin/env python3
"""Construye las páginas de autos del sitio a partir de las fichas.

Lee   ~/Documents/Github/pacifico-auto/autos/<auto>/ficha.md + fotos/
Crea  autos/index.html (lista) y autos/<auto>/index.html (detalle) en esta carpeta.

Uso:  python3 build.py            -> solo autos reales
      python3 build.py --ejemplo  -> incluye también las carpetas _ejemplo-*
      python3 build.py --borrador -> construye en _borrador/ (fuera de Git) incluyendo autos en borrador

No borra nada y no publica nada: solo escribe archivos en esta carpeta.
"""
import html
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

WEB = Path(__file__).resolve().parent
AUTOS = WEB.parent / "pacifico-auto" / "autos"
OUT = WEB / "autos"
BORRADOR = WEB / "_borrador"  # vista previa local; está en .gitignore
WHATSAPP = "50689505551"
FOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".svg", ".webp"}
ESTADOS = {
    "disponible": ("Available", "Disponible"),
    "reservado": ("Reserved", "Reservado"),
    "vendido": ("Sold", "Vendido"),
    "borrador": ("Draft", "Borrador"),
}
CAMPOS = [  # (clave, EN, ES)
    ("año", "Year", "Año"),
    ("km", "Mileage", "Kilometraje"),
    ("transmision", "Transmission", "Transmisión"),
    ("combustible", "Fuel", "Combustible"),
    ("traccion", "Drivetrain", "Tracción"),
    ("suspension", "Suspension", "Suspensión"),
    ("color", "Colour", "Color"),
    ("dueños", "Owners", "Dueños"),
    ("ubicacion", "Location", "Ubicación"),
    ("inspeccion", "Inspected", "Inspeccionado"),
]
e = html.escape


def leer_ficha(path):
    """Frontmatter simple 'clave: valor' + secciones '## ES' y '## EN'."""
    texto = path.read_text(encoding="utf-8")
    datos, cuerpo = {}, texto
    if texto.startswith("---"):
        _, fm, cuerpo = texto.split("---", 2)
        for linea in fm.strip().splitlines():
            if ":" in linea:
                k, v = linea.split(":", 1)
                datos[k.strip()] = v.strip()
    secciones, actual = {}, None
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            actual = linea[3:].strip().lower()
            secciones[actual] = []
        elif actual:
            secciones[actual].append(linea)
    return datos, secciones


def cuerpo_html(lineas):
    out, en_lista = [], False
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith("- "):
            if not en_lista:
                out.append("<ul>")
                en_lista = True
            out.append("<li>%s</li>" % e(linea[2:]))
        else:
            if en_lista:
                out.append("</ul>")
                en_lista = False
            if linea:
                out.append("<p>%s</p>" % e(linea))
    if en_lista:
        out.append("</ul>")
    return "\n".join(out)


def miles(v):
    try:
        return "{:,}".format(int(str(v).replace(",", "").replace(".", "")))
    except ValueError:
        return str(v)


def preparar_fotos(origen, destino):
    """Copia las fotos al sitio; convierte a JPG de máx. 1600 px con sips."""
    destino.mkdir(parents=True, exist_ok=True)
    nombres = []
    if not origen.is_dir():
        return nombres
    for f in sorted(origen.iterdir()):
        ext = f.suffix.lower()
        if ext not in FOTO_EXT or f.name.startswith("."):
            continue
        if ext == ".svg":
            salida = destino / f.name
            shutil.copyfile(f, salida)
        else:
            salida = destino / (f.stem + ".jpg")
            if not salida.exists() or salida.stat().st_mtime < f.stat().st_mtime:
                subprocess.run(
                    ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80",
                     "-Z", "1600", str(f), "--out", str(salida)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        nombres.append(salida.name)
    return nombres


def bi(en, es, tag="span"):
    return '<%s class="en">%s</%s><%s class="es">%s</%s>' % (tag, en, tag, tag, es, tag)


def pagina(titulo, contenido, raiz, ejemplo=False, borrador=False):
    aviso = ('<p class="aviso-ejemplo">MUESTRA — datos y fotos de ejemplo, este auto no existe</p>'
             if ejemplo else "")
    if borrador:
        aviso += '<p class="aviso-ejemplo">BORRADOR — vista previa en este Mac, no publicar</p>'
    return """<!DOCTYPE html>
<html lang="en" class="lang-en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} — Pacífico Auto</title>
<link rel="icon" href="{r}img/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}css/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{r}index.html" aria-label="Pacífico Auto">
    <img src="{r}img/icon.svg" alt="" width="40" height="40"><span>Pacífico Auto</span>
  </a>
  <nav>
    <a href="{r}autos/index.html">{cars}</a>
    <a href="{r}index.html#services">{serv}</a>
    <a href="{r}index.html#how">{how}</a>
    <a href="{r}index.html#contact">{cont}</a>
  </nav>
  <button class="lang-toggle" type="button" aria-label="Cambiar idioma / Switch language">
    <span class="en">ES</span><span class="es">EN</span>
  </button>
</header>
{aviso}
<main>
{contenido}
</main>
<footer>
  <p>© <span id="year">2026</span> Pacífico Auto · Guanacaste · Nicoya · Puntarenas · Costa Rica</p>
  <p class="social"><a href="https://www.instagram.com/pacificoauto.cr/" target="_blank" rel="noopener">Instagram @pacificoauto.cr</a> · <a href="https://www.facebook.com/profile.php?id=61596536469097" target="_blank" rel="noopener">Facebook</a></p>
</footer>
<script src="{r}js/main.js"></script>
</body>
</html>
""".format(titulo=e(titulo), r=raiz, aviso=aviso, contenido=contenido,
           cars=bi("Cars", "Autos"), serv=bi("Services", "Servicios"),
           how=bi("How it works", "Cómo funciona"), cont=bi("Contact", "Contacto"))


def construir(con_ejemplo, con_borrador=False):
    global OUT
    if con_borrador:
        # Copia el sitio a _borrador/ y construye ahí: los borradores nunca tocan el sitio real.
        BORRADOR.mkdir(exist_ok=True)
        for nombre in ("css", "img", "js"):
            shutil.copytree(WEB / nombre, BORRADOR / nombre, dirs_exist_ok=True)
        shutil.copyfile(WEB / "index.html", BORRADOR / "index.html")
        OUT = BORRADOR / "autos"
    autos = []
    for carpeta in sorted(AUTOS.iterdir()):
        ficha = carpeta / "ficha.md"
        if not ficha.is_file() or carpeta.name == "_plantilla":
            continue
        ejemplo = carpeta.name.startswith("_")
        if ejemplo and not con_ejemplo:
            continue
        d, sec = leer_ficha(ficha)
        estado = d.get("estado", "disponible").lower()
        if estado == "borrador" and not con_borrador:
            continue
        slug = carpeta.name.lstrip("_")
        fotos = preparar_fotos(carpeta / "fotos", OUT / slug / "fotos")
        nombre = " ".join(x for x in (d.get("año"), d.get("marca"), d.get("modelo"), d.get("version")) if x)
        est_en, est_es = ESTADOS.get(estado, ESTADOS["disponible"])
        # Si hay los dos precios se muestran ambos: dólares primero, colones después.
        precio = " · ".join(x for x in (
            "$" + miles(d["precio_usd"]) if d.get("precio_usd") else "",
            "₡" + miles(d["precio_crc"]) if d.get("precio_crc") else "") if x)
        autos.append(dict(d=d, sec=sec, slug=slug, fotos=fotos, nombre=nombre, estado=estado,
                          est_en=est_en, est_es=est_es, precio=precio, ejemplo=ejemplo))

    OUT.mkdir(exist_ok=True)
    for a in autos:
        d = a["d"]
        filas = []
        for clave, en, es in CAMPOS:
            v = d.get(clave)
            if not v:
                continue
            if clave == "km":
                v = miles(v) + " km"
            filas.append("<div><dt>%s</dt><dd>%s</dd></div>" % (bi(en, es), e(v)))
        if a["fotos"]:
            galeria = '<div class="galeria"><img id="foto-principal" src="fotos/%s" alt="%s">' % (
                quote(a["fotos"][0]), e(a["nombre"]))
            galeria += '<div class="thumbs">' + "".join(
                '<img src="fotos/%s" alt="" loading="lazy">' % quote(f) for f in a["fotos"]) + "</div></div>"
        else:
            galeria = '<div class="galeria sin-fotos">%s</div>' % bi("Photos coming soon", "Fotos pronto")
        msg_en = "Hi Agustín, I'd like to reserve / see the %s (%s)." % (a["nombre"], a["precio"])
        msg_es = "Hola Agustín, quiero reservar / ver el %s (%s)." % (a["nombre"], a["precio"])
        if a["estado"] == "vendido":
            cta = '<p class="muted">%s</p>' % bi(
                "This one is sold. Message me and I'll find you one like it.",
                "Este ya se vendió. Escríbame y le busco uno igual.")
            msg_en = "Hi Agustín, I'm looking for a car like the %s." % a["nombre"]
            msg_es = "Hola Agustín, busco un auto como el %s." % a["nombre"]
            txt_en, txt_es = "Find me one like it", "Búsqueme uno igual"
        else:
            cta = ""
            txt_en, txt_es = "Reserve on WhatsApp", "Reservar por WhatsApp"
        wa = "https://wa.me/%s?text=" % WHATSAPP
        botones = ('<a class="btn primary en" href="%s" target="_blank" rel="noopener">%s</a>'
                   '<a class="btn primary es" href="%s" target="_blank" rel="noopener">%s</a>') % (
            wa + quote(msg_en), txt_en, wa + quote(msg_es), txt_es)
        contenido = """<section class="auto">
  <p class="migas"><a href="../index.html">← {todos}</a></p>
  <div class="auto-cols">
    {galeria}
    <div class="auto-info">
      <span class="estado {estado}">{est}</span>
      <h1>{nombre}</h1>
      <p class="precio">{precio}</p>
      <dl class="ficha">{filas}</dl>
      {cta}
      <div class="cta">{botones}</div>
      <p class="muted small">{nota}</p>
    </div>
  </div>
  <div class="auto-texto">
    <div class="en">{en}</div><div class="es">{es}</div>
  </div>
</section>""".format(
            todos=bi("All cars", "Todos los autos"), galeria=galeria, estado=a["estado"],
            est=bi(a["est_en"], a["est_es"]), nombre=e(a["nombre"]), precio=e(a["precio"]),
            filas="".join(filas), cta=cta, botones=botones,
            nota=bi("I'm a broker: the car belongs to its owner. Reserving means I hold it for you and set up the viewing.",
                    "Soy intermediario: el auto es de su dueño. Reservar significa que se lo aparto y coordino la visita."),
            en=cuerpo_html(a["sec"].get("en", [])), es=cuerpo_html(a["sec"].get("es", [])))
        (OUT / a["slug"]).mkdir(parents=True, exist_ok=True)
        (OUT / a["slug"] / "index.html").write_text(
            pagina(a["nombre"], contenido, "../../", a["ejemplo"], a["estado"] == "borrador"), encoding="utf-8")

    def tarjeta(a):
        d = a["d"]
        img = ('<img src="%s/fotos/%s" alt="%s" loading="lazy">' % (a["slug"], quote(a["fotos"][0]), e(a["nombre"]))
               if a["fotos"] else '<div class="sin-foto"></div>')
        sub = " · ".join(x for x in (miles(d["km"]) + " km" if d.get("km") else "",
                                     d.get("transmision", ""), d.get("ubicacion", "")) if x)
        return """<a class="auto-card {estado}" href="{slug}/index.html">
  {img}
  <span class="estado {estado}">{est}</span>
  <h3>{nombre}</h3>
  <p class="muted small">{sub}</p>
  <p class="precio">{precio}</p>
</a>""".format(slug=a["slug"], img=img, estado=a["estado"], est=bi(a["est_en"], a["est_es"]),
               nombre=e(a["nombre"]), sub=e(sub), precio=e(a["precio"]))

    # Dos secciones: en venta (disponibles y reservados) y vendidos. Los más nuevos primero.
    orden = {"disponible": 0, "reservado": 1, "borrador": 2}
    en_venta = sorted((a for a in autos if a["estado"] != "vendido"),
                      key=lambda a: a["d"].get("publicado", ""), reverse=True)
    en_venta.sort(key=lambda a: orden.get(a["estado"], 0))  # estable: disponibles primero
    vendidos = sorted((a for a in autos if a["estado"] == "vendido"),
                      key=lambda a: a["d"].get("vendido") or a["d"].get("publicado", ""), reverse=True)
    tarjetas = [tarjeta(a) for a in en_venta]
    if not tarjetas:
        tarjetas.append('<p class="center muted">%s</p>' % bi(
            "No cars listed right now. Message me and I'll find yours.",
            "No hay autos publicados ahora. Escríbame y le busco el suyo."))
    lista = """<section>
  <h2>{t}</h2>
  <p class="center muted">{s}</p>
  <div class="grid autos">{tarjetas}</div>
</section>""".format(
        t=bi("Cars for sale", "Autos en venta"),
        s=bi("One owner · clean title · no accidents. Each one inspected by me.",
             "Un dueño · título limpio · sin accidentes. Cada uno revisado por mí."),
        tarjetas="\n".join(tarjetas))
    if vendidos:
        lista += """
<section class="vendidos" id="vendidos">
  <h2>{t}</h2>
  <p class="center muted">{s}</p>
  <div class="grid autos">{tarjetas}</div>
</section>""".format(
            t=bi("Sold", "Vendidos"),
            s=bi("Cars I've already sold. Want one like these? Message me and I'll find it.",
                 "Autos que ya vendí. ¿Quiere uno así? Escríbame y se lo busco."),
            tarjetas="\n".join(tarjeta(a) for a in vendidos))
    (OUT / "index.html").write_text(
        pagina("Cars / Autos", lista, "../", any(a["ejemplo"] for a in autos), any(a["estado"] == "borrador" for a in autos)), encoding="utf-8")
    return autos


if __name__ == "__main__":
    hechos = construir("--ejemplo" in sys.argv, "--borrador" in sys.argv)
    print("Autos construidos: %d" % len(hechos))
    for a in hechos:
        print("  - %s  [%s]  %d fotos%s" % (a["nombre"], a["estado"], len(a["fotos"]),
                                             "  (EJEMPLO)" if a["ejemplo"] else ""))
