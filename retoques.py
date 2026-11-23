"""Retoques finales de la web de Zaragüela (se ejecuta después de construir.py).
- Formulario de contacto: envía los mensajes a hola@zaraguela.es (Web3Forms).
- Email de contacto visible: hola@zaraguela.es
- Zagalejos: añade "Incluye faltriquera a juego" a las características (si no la mencionan ya).
- Textos generales: sin "100% artesanal" ni "hecho a mano".
- Fotos: la web muestra una versión ligera; al tocar la foto se abre el ORIGINAL intacto.
  Los originales nunca se modifican.
"""
import glob, os, sys, subprocess, json
RAIZ = os.path.dirname(os.path.abspath(__file__))
CLAVE = '0f424496-0f25-4064-9c37-24830ef9fe17'
EMAIL = 'hola@zaraguela.es'

VIEJO = "location.href='mailto:zaraguela@icloud.com?subject='+encodeURIComponent('Consulta desde la web - '+v('name'))+'&body='+encodeURIComponent(body);"
NUEVO = ("var b=f.querySelector('button[type=submit]'),m=f.querySelector('[data-form-msg]');"
 "if(!m){m=document.createElement('p');m.setAttribute('data-form-msg','');m.className='text-sm text-center text-brand-brown';m.setAttribute('role','status');f.appendChild(m);}"
 "b.disabled=true;m.textContent='Enviando…';"
 "fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},"
 "body:JSON.stringify({access_key:'" + CLAVE + "',subject:'Consulta desde la web - '+v('name'),from_name:'Web Zaragüela',"
 "nombre:v('name'),email:v('email'),telefono:v('phone'),message:v('message')})})"
 ".then(function(r){return r.json();}).then(function(j){if(!j.success)throw 0;"
 "m.textContent='¡Gracias! Hemos recibido tu mensaje y te contestaremos muy pronto.';f.reset();})"
 ".catch(function(){m.textContent='No se ha podido enviar. Escríbenos a " + EMAIL + "';})"
 ".then(function(){b.disabled=false;});")

FIN_LISTA = '</ul></div><div class="space-y-3">'
FALTRIQUERA = '<li class="flex items-start gap-3"><span class="w-1.5 h-1.5 rounded-full bg-brand-wine mt-2 flex-shrink-0"></span>Incluye faltriquera a juego</li>'

TEXTOS = [
    ('Taller propio 100% artesanal en Murcia. Piezas únicas hechas a mano.', 'Taller propio en Murcia. Piezas únicas, con detalles hechos a mano.'),
    ('Taller propio 100% artesanal en Murcia.', 'Taller propio en Murcia.'),
    ('>100% Artesanal<', '>Taller propio en Murcia<'),
    ('Piezas únicas hechas de manera artesanal en nuestro taller de Murcia.', 'Piezas únicas confeccionadas en nuestro taller de Murcia.'),
    ('>Taller Propio</h3>', '>Taller propio</h3>'),
    ('100% artesanal. Cada zagalejo es cortado y cosido en nuestro taller de Murcia con técnicas tradicionales.', 'Cada zagalejo se corta y se cose en nuestro taller de Murcia, con técnicas tradicionales.'),
    ('Cada pieza es única y está hecha a mano en nuestro taller de Murcia.', 'Cada pieza es única y está confeccionada en nuestro taller de Murcia.'),
]

# ---------- FOTOS: versión ligera para mostrar, original intacto para ampliar ----------
LIGERA_MAX = 2000      # píxeles del lado largo
LIGERA_CALIDAD = 90    # calidad JPEG (sin perder color: submuestreo 4:4:4)
MINIMO_KB = 400        # las fotos más pequeñas que esto no se tocan

def preparar_fotos():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 'pillow'])
        try:
            from PIL import Image, ImageOps
        except ImportError:
            print('AVISO: no se pudo instalar Pillow; se usan las fotos originales'); return {}
    origen = os.path.join(RAIZ, 'public', 'fotos')
    destino = os.path.join(origen, 'web')
    os.makedirs(destino, exist_ok=True)
    mapa = {}
    for nombre in sorted(os.listdir(origen)):
        ruta = os.path.join(origen, nombre)
        if not os.path.isfile(ruta) or not nombre.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        if os.path.getsize(ruta) < MINIMO_KB * 1024:
            continue
        try:
            im = Image.open(ruta)
            im = ImageOps.exif_transpose(im)
            if im.mode in ('RGBA', 'LA', 'P'):
                rgba = im.convert('RGBA')
                if rgba.getextrema()[3][0] < 250:   # tiene transparencia (logos): no se toca
                    continue
                im = rgba
            im = im.convert('RGB')
            im.thumbnail((LIGERA_MAX, LIGERA_MAX), Image.LANCZOS)
            salida = os.path.join(destino, os.path.splitext(nombre)[0] + '.jpg')
            im.save(salida, 'JPEG', quality=LIGERA_CALIDAD, subsampling=0, optimize=True, progressive=True)
            if os.path.getsize(salida) > os.path.getsize(ruta) * 0.8:   # no compensa
                os.remove(salida); continue
            mapa['fotos/' + nombre] = 'fotos/web/' + os.path.splitext(nombre)[0] + '.jpg'
        except Exception as err:
            print('AVISO foto', nombre, err)
    print('Fotos ligeras preparadas:', len(mapa))
    return mapa

ZOOM = """<style>[data-gal=main],button.break-inside-avoid img{cursor:zoom-in}</style><script>(function(){
document.addEventListener('click',function(e){var im=e.target.closest('[data-gal=main]');if(!im)return;
var src=im.getAttribute('src'),o=null;document.querySelectorAll('img[data-original]').forEach(function(x){if(!o&&x.getAttribute('src')===src)o=x.getAttribute('data-original');});
if(!o)o=im.getAttribute('data-original')||src;
var ov=document.createElement('div');ov.style.cssText='position:fixed;inset:0;z-index:200;background:rgba(30,12,8,.96);overflow:auto;-webkit-overflow-scrolling:touch;text-align:center';
ov.innerHTML='<button aria-label="Cerrar" style="position:fixed;top:14px;right:14px;z-index:2;width:44px;height:44px;border-radius:50%;border:0;background:rgba(245,237,224,.25);color:#f5ede0;font-size:26px;cursor:pointer">×</button><p style="color:#f5ede0;font:14px sans-serif;margin:14px 60px">Cargando la foto en alta calidad… Toca la foto para ver el detalle</p><img alt="" style="max-width:100%;max-height:85vh;cursor:zoom-in;display:block;margin:0 auto">';
var big=ov.querySelector('img'),p=ov.querySelector('p');big.alt=im.alt||'';big.onload=function(){p.textContent='Toca la foto para ver el detalle';};big.src=o;
big.onclick=function(ev){ev.stopPropagation();if(big.style.maxWidth==='none'){big.style.maxWidth='100%';big.style.maxHeight='85vh';big.style.cursor='zoom-in';}else{big.style.maxWidth='none';big.style.maxHeight='none';big.style.cursor='zoom-out';}};
function close(){ov.remove();document.removeEventListener('keydown',esc);}function esc(k){if(k.key==='Escape')close();}
ov.onclick=function(ev){if(ev.target===ov||ev.target.closest('button'))close();};document.addEventListener('keydown',esc);document.body.appendChild(ov);});
})();</script>"""

MAPA = preparar_fotos()

n = 0
for f in glob.glob(os.path.join(RAIZ, 'public', '*.html')):
    s = open(f, encoding='utf-8').read()
    t = s.replace(VIEJO, NUEVO).replace('zaraguela@icloud.com', EMAIL)
    for viejo, nuevo in TEXTOS:
        t = t.replace(viejo, nuevo)
    if MAPA:
        for orig, ligera in MAPA.items():
            t = t.replace('src="' + orig + '"', 'src="' + ligera + '" data-original="' + orig + '"')
        t = t.replace('big.src=img.src;', "big.src=img.getAttribute('data-original')||img.src;")
        if '</body>' in t and 'data-gal=main],button' not in t:
            t = t.replace('</body>', ZOOM + '</body>', 1)
    if os.path.basename(f).startswith('zagalejos-') and FIN_LISTA in t:
        lista = t[t.find('Características</h3>'):t.find(FIN_LISTA)]
        if 'faltriquera' not in lista.lower():
            t = t.replace(FIN_LISTA, FALTRIQUERA + FIN_LISTA, 1)
    if t != s:
        open(f, 'w', encoding='utf-8').write(t); n += 1
print('Retoques aplicados en', n, 'páginas')
