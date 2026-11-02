"""Construye la web de Zaragüela en la carpeta public/.

Lee los productos de productos/*.json (los que se editan desde el panel),
las páginas de plantillas/ y copia las fotos tal cual, sin tocarlas.
Cloudflare lo ejecuta solo cada vez que hay un cambio.
"""
import glob, html, json, os, re, shutil, unicodedata

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, 'public')

CATEGORIAS = {  # categoría -> (grupo, página del listado)
    'Zagalejos': ('Güertanas', 'zagalejos.html'),
    'Picos': ('Güertanas', 'picos.html'),
    'Delantales': ('Güertanas', 'delantales.html'),
    'Chalecos': ('Güertanos', 'chalecos.html'),
    'Zaragüeles': ('Güertanos', 'zaragueles.html'),
}
ESTADO_TARJETA = {'Disponible': 'bg-brand-olive/90 text-white', 'Bajo pedido': 'bg-brand-gold/90 text-white', 'Agotado': 'bg-brand-wine/90 text-white'}
ESTADO_FICHA = {'Disponible': 'bg-brand-olive/10 text-brand-olive', 'Bajo pedido': 'bg-brand-gold/10 text-brand-gold', 'Agotado': 'bg-brand-wine/10 text-brand-wine'}
CARACT_ZAG = ['Confeccionado en nuestro taller en el corazón de la Huerta Murciana', 'Personalizable: elige telas, colores y detalles de acabado a tu gusto',
              'Zagalejo único — no encontrarás otro igual', 'Ideal para el Bando de la Huerta y eventos tradicionales']
CARACT = ['Confeccionado 100% a mano en nuestro taller de Murcia', 'Personalizable: elige telas, colores y detalles de acabado',
          'Pieza única — no encontrarás otra igual', 'Ideal para el Bando de la Huerta y eventos tradicionales']

ARROW_L = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left w-5 h-5" aria-hidden="true"><path d="m15 18-6-6 6-6"></path></svg>'
ARROW_R = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right w-5 h-5" aria-hidden="true"><path d="m9 18 6-6-6-6"></path></svg>'
BACK = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-left w-4 h-4" aria-hidden="true"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>'
MSG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-message-circle w-4 h-4" aria-hidden="true"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"></path></svg>'

e = html.escape
def slug(t): return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', t.lower()).encode('ascii', 'ignore').decode()).strip('-')
def foto(ruta): return 'fotos/' + os.path.basename(ruta)  # todas las fotos se publican en fotos/

def leer_productos():
    prods = []
    # productos/ (los del panel) y también los .json sueltos en la raíz
    for f in sorted(glob.glob(os.path.join(RAIZ, 'productos', '*.json')) + glob.glob(os.path.join(RAIZ, '*.json'))):
        try:
            p = json.load(open(f, encoding='utf-8'))
        except Exception as err:
            print('AVISO: no se pudo leer', f, err); continue
        if not isinstance(p, dict): continue
        if not p.get('nombre') or p.get('categoria') not in CATEGORIAS:
            print('AVISO: producto sin nombre o categoría, se omite:', f); continue
        if p.get('oculto'): continue
        p['fotos'] = [foto(x) for x in (p.get('fotos') or []) if x]
        if not p['fotos']:
            print('AVISO: producto sin fotos, se omite:', p['nombre']); continue
        p.setdefault('estado', 'Disponible'); p.setdefault('precio', '')
        p['grupo'], p['pagina_cat'] = CATEGORIAS[p['categoria']]
        p['archivo'] = slug(p['categoria']) + '-' + slug(p['nombre']) + '.html'
        prods.append(p)
    prods.sort(key=lambda p: (float(p.get('orden') or 999), p['nombre']))
    return prods

def tarjeta(p):
    estado = p['estado']
    return (f'<a class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-500" href="{p["archivo"]}">'
            f'<div class="aspect-[4/5] overflow-hidden relative"><img alt="{e(p["nombre"])}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" src="{e(p["fotos"][0])}">'
            f'<div class="absolute top-4 left-4"><span class="px-3 py-1 rounded-full text-xs uppercase tracking-wider font-medium {ESTADO_TARJETA.get(estado, ESTADO_TARJETA["Disponible"])}">{e(estado)}</span></div></div>'
            f'<div class="p-6"><span class="text-xs uppercase tracking-wider text-brand-gold font-medium">{e(p["categoria"])}</span>'
            f'<h3 class="text-lg font-bold text-brand-brown mt-1 group-hover:text-brand-wine transition-colors" style="font-family: Georgia, serif;">{e(p["nombre"])}</h3>'
            f'<p class="text-brand-brown/50 text-sm mt-2 line-clamp-2">{e(p.get("descripcion") or "")}</p>'
            f'<div class="flex items-center justify-between mt-4 pt-4 border-t border-brand-cream"><span class="text-xl font-bold text-brand-wine">{e(p["precio"])}</span>'
            f'<span class="text-xs text-brand-wine uppercase tracking-wider group-hover:translate-x-1 transition-transform">Ver detalles →</span></div></div></a>')

def tarjeta_destacada(p):
    return (f'<a class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-500" href="{p["archivo"]}">'
            f'<div class="aspect-[4/5] overflow-hidden"><img alt="{e(p["nombre"])}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" src="{e(p["fotos"][0])}"></div>'
            f'<div class="p-6"><h3 class="text-lg font-bold text-brand-brown group-hover:text-brand-wine transition-colors" style="font-family: Georgia, serif;">{e(p["nombre"])}</h3>'
            f'<div class="flex items-center justify-between mt-2"><span class="text-brand-gold font-semibold">{e(p["precio"])}</span>'
            f'<span class="text-xs uppercase tracking-wider text-brand-brown/40">{e(p["estado"])}</span></div></div></a>')

def ficha(p):
    gal = p['fotos']; n = len(gal); name = e(p['nombre'])
    alts = [name if i == 0 else f'{name} - foto {i+1}' for i in range(n)]
    nav = thumbs = ''
    if n > 1:
        nav = (f'<button class="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center text-brand-brown hover:bg-white transition-all opacity-0 group-hover:opacity-100 shadow-md" aria-label="Foto anterior" data-gal="prev">{ARROW_L}</button>'
               f'<button class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center text-brand-brown hover:bg-white transition-all opacity-0 group-hover:opacity-100 shadow-md" aria-label="Foto siguiente" data-gal="next">{ARROW_R}</button>'
               f'<div class="absolute bottom-3 right-3 px-3 py-1 rounded-full bg-black/40 backdrop-blur-sm text-white text-xs font-medium" data-gal="count">1 / {n}</div>')
        thumbs = '<div class="grid grid-cols-4 sm:grid-cols-5 gap-2">' + ''.join(
            f'<button class="aspect-[3/4] rounded-xl overflow-hidden transition-all {"ring-2 ring-brand-wine ring-offset-2 ring-offset-brand-cream shadow-md" if i == 0 else "opacity-60 hover:opacity-100"}" data-gal-thumb="{i}"><img alt="{alts[i]}" class="w-full h-full object-cover" src="{e(g)}"></button>'
            for i, g in enumerate(gal)) + '</div>'
    caract = [c for c in (p.get('caracteristicas') or []) if c and c.strip()] or (CARACT_ZAG if p['categoria'] == 'Zagalejos' else CARACT)
    return (
        f'<div class="pt-28 pb-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">'
        f'<a class="inline-flex items-center gap-2 text-brand-brown/60 hover:text-brand-wine transition-colors mb-8 text-sm" href="{p["pagina_cat"]}">{BACK}Volver a {e(p["categoria"])}</a>'
        f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12"><div class="space-y-4" data-gallery=\'{e(json.dumps(gal))}\'>'
        f'<div class="relative bg-white rounded-2xl overflow-hidden shadow-sm group"><img alt="{alts[0]}" class="w-full h-auto object-contain transition-opacity duration-300" data-gal="main" src="{e(gal[0])}">{nav}</div>{thumbs}</div>'
        f'<div class="lg:pt-4"><span class="text-xs uppercase tracking-widest text-brand-gold font-semibold">{p["grupo"]} · {e(p["categoria"])}</span>'
        f'<h1 class="text-3xl sm:text-4xl font-bold text-brand-brown mt-2 mb-4" style="font-family: Georgia, serif;">{name}</h1>'
        f'<div class="flex items-center gap-4 mb-6"><span class="text-3xl font-bold text-brand-wine">{e(p["precio"])}</span>'
        f'<span class="px-3 py-1 rounded-full text-xs uppercase tracking-wider font-medium {ESTADO_FICHA.get(p["estado"], ESTADO_FICHA["Disponible"])}">{e(p["estado"])}</span></div>'
        f'<div class="border-t border-brand-cream pt-6 mb-8"><p class="text-brand-brown/70 leading-relaxed text-lg" style="white-space:pre-line">{e(p.get("descripcion") or "")}</p></div>'
        f'<div class="bg-white rounded-2xl p-6 mb-8 space-y-4"><h3 class="font-semibold text-brand-brown text-sm uppercase tracking-wider">Características</h3><ul class="space-y-3 text-sm text-brand-brown/70">'
        + ''.join(f'<li class="flex items-start gap-3"><span class="w-1.5 h-1.5 rounded-full bg-brand-wine mt-2 flex-shrink-0"></span>{e(c)}</li>' for c in caract) +
        f'</ul></div><div class="space-y-3"><a class="w-full inline-flex items-center justify-center gap-2 px-8 py-4 bg-brand-wine text-brand-cream rounded-full text-sm uppercase tracking-wider font-medium hover:bg-brand-wine-light transition-all hover:shadow-lg hover:shadow-brand-wine/20" href="contacto.html">{MSG}Consultar / Hacer pedido</a>'
        f'<a href="https://www.instagram.com/zaraguela" target="_blank" rel="noopener noreferrer" class="w-full inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-brand-wine/20 text-brand-wine rounded-full text-sm uppercase tracking-wider font-medium hover:bg-brand-wine/5 transition-all">Ver más en Instagram</a></div></div></div></div>')

def main():
    shutil.rmtree(SALIDA, ignore_errors=True)
    os.makedirs(SALIDA)
    # fotos originales, sin tocar: las de fotos/ y las sueltas en la raíz
    os.makedirs(os.path.join(SALIDA, 'fotos'))
    for d in (RAIZ, os.path.join(RAIZ, 'fotos')):
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic', '.avif')):
                shutil.copyfile(os.path.join(d, f), os.path.join(SALIDA, 'fotos', f))
    shutil.copyfile(os.path.join(RAIZ, 'estilos.css'), os.path.join(SALIDA, 'estilos.css'))
    prods = leer_productos()
    # las plantillas pueden estar en plantillas/ o sueltas en la raíz
    PL = os.path.join(RAIZ, 'plantillas') if os.path.isdir(os.path.join(RAIZ, 'plantillas')) else RAIZ
    plantilla_ficha = open(os.path.join(PL, 'producto.html'), encoding='utf-8').read()
    paginas_cat = {pag: cat for cat, (_, pag) in CATEGORIAS.items()}
    for f in sorted(os.listdir(PL)):
        if not f.endswith('.html') or f == 'producto.html': continue
        s = open(os.path.join(PL, f), encoding='utf-8').read()
        if f in paginas_cat:
            s = s.replace('<!--PRODUCTOS-->', ''.join(tarjeta(p) for p in prods if p['categoria'] == paginas_cat[f]))
        elif f == 'index.html':
            s = s.replace('<!--PRODUCTOS-->', ''.join(tarjeta_destacada(p) for p in prods if p.get('destacado')))
        open(os.path.join(SALIDA, f), 'w', encoding='utf-8').write(s)
    for p in prods:
        s = plantilla_ficha.replace('<!--FICHA-->', ficha(p)).replace('<!--TITULO-->', e(p['nombre']) + ' — Zaragüela')
        open(os.path.join(SALIDA, p['archivo']), 'w', encoding='utf-8').write(s)
    print('Web construida:', len(prods), 'productos')

if __name__ == '__main__':
    main()
