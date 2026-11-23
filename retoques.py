"""Retoques finales de la web de Zaragüela (se ejecuta después de construir.py).
- Formulario de contacto: envía los mensajes a hola@zaraguela.es (Web3Forms).
- Email de contacto visible: hola@zaraguela.es
- Zagalejos: añade "Incluye faltriquera a juego" a las características (si no la mencionan ya).
- Textos generales: sin "100% artesanal" ni "hecho a mano".
"""
import glob, os
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

n = 0
for f in glob.glob(os.path.join(RAIZ, 'public', '*.html')):
    s = open(f, encoding='utf-8').read()
    t = s.replace(VIEJO, NUEVO).replace('zaraguela@icloud.com', EMAIL)
    for viejo, nuevo in TEXTOS:
        t = t.replace(viejo, nuevo)
    if os.path.basename(f).startswith('zagalejos-') and FIN_LISTA in t:
        lista = t[t.find('Características</h3>'):t.find(FIN_LISTA)]
        if 'faltriquera' not in lista.lower():
            t = t.replace(FIN_LISTA, FALTRIQUERA + FIN_LISTA, 1)
    if t != s:
        open(f, 'w', encoding='utf-8').write(t); n += 1
print('Retoques aplicados en', n, 'páginas')
