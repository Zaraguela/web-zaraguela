"""Retoques finales de la web de Zaragüela (se ejecuta después de construir.py).
- Formulario de contacto: envía los mensajes a hola@zaraguela.es (Web3Forms).
- Email de contacto visible: hola@zaraguela.es
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

n = 0
for f in glob.glob(os.path.join(RAIZ, 'public', '*.html')):
    s = open(f, encoding='utf-8').read()
    t = s.replace(VIEJO, NUEVO).replace('zaraguela@icloud.com', EMAIL)
    if t != s:
        open(f, 'w', encoding='utf-8').write(t); n += 1
print('Retoques aplicados en', n, 'páginas')
