
document.documentElement.classList.add('js');
document.addEventListener('DOMContentLoaded',()=>{
  // Scroll to top on page load (evita que el ancla quede a mitad)
  if(location.hash){history.scrollRestoration='manual';requestAnimationFrame(()=>window.scrollTo(0,0))}
  // Menú hamburguesa
  const b=document.querySelector('.hamb'),m=document.querySelector('.menu');
  if(b&&m){b.addEventListener('click',()=>{const o=m.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')});document.addEventListener('click',e=>{if(!m.contains(e.target)&&!b.contains(e.target)&&m.classList.contains('open')){m.classList.remove('open');b.setAttribute('aria-expanded','false')}})}
  // Reveal on scroll (un único IntersectionObserver compartido)
  const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-visible');obs.unobserve(e.target)}}),{threshold:.08});
  document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
  // Lightbox de imágenes
  document.querySelectorAll('[data-lightbox]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const o=document.createElement('div');o.style='position:fixed;inset:0;background:rgba(0,0,0,.86);z-index:99;display:grid;place-items:center;padding:2rem;cursor:pointer';o.innerHTML='<img src="'+a.href+'" alt="" style="max-height:90vh;border-radius:1rem;border:1px solid #2A3142">';o.onclick=()=>o.remove();document.body.append(o)}));
  // Prefetch de páginas en hover (acelera la navegación interna)
  const prefetched=new Set();
  function prefetch(url){if(prefetched.has(url))return;prefetched.add(url);const l=document.createElement('link');l.rel='prefetch';l.href=url;l.as='document';document.head.appendChild(l)}
  document.querySelectorAll('a[href^="/"],a[href^="./"],a[href^="../"],a:not([href^="http"]):not([href^="tel"]):not([href^="mailto"]):not([href^="#"])').forEach(a=>{
    let armed=false;
    const arm=()=>{if(armed)return;armed=true;try{prefetch(new URL(a.getAttribute('href'),location.href).href)}catch(_){}}
    a.addEventListener('mouseenter',arm,{passive:true});
    a.addEventListener('focus',arm,{passive:true});
    a.addEventListener('touchstart',arm,{passive:true});
  });
  // Botón scroll-to-top
  const stt=document.createElement('button');
  stt.id='scroll-top';stt.setAttribute('aria-label','Volver al inicio de la página');stt.innerHTML='\u2191';
  document.body.appendChild(stt);
  let sttTicking=false;let sttShown=false;
  const togStt=()=>{const should=window.scrollY>500;if(should!==sttShown){sttShown=should;stt.classList.toggle('show',should)}sttTicking=false};
  window.addEventListener('scroll',()=>{if(!sttTicking){sttTicking=true;requestAnimationFrame(togStt)}},{passive:true});
  togStt();
  stt.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
  // Logo/brand: al hacer clic, scroll suave arriba si ya estás en home
  document.querySelectorAll('.brand,.brand-title').forEach(el=>{
    el.addEventListener('click',e=>{
      const href=el.getAttribute('href');
      if(!href)return;
      const u=new URL(href,location.href);
      if(u.pathname===location.pathname){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})}
    });
  });
  // Banner de cookies (RGPD) - desaparece al scrollear
  if(!localStorage.getItem('galaxia_cookies_ok')){
    const c=document.createElement('div');c.id='cookie-banner';
    c.innerHTML='<p><span class="cb-icon" aria-hidden="true">🍪</span><span class="cb-full">Usamos cookies técnicas necesarias para el funcionamiento del sitio. No usamos cookies de seguimiento ni de terceros. <a href="/cookies/" aria-label="Ver Política de Cookies completa">Ver Política de Cookies</a>.</span><span class="cb-short"><a href="/cookies/" aria-label="Ver Política de Cookies">Cookies técnicas</a></span></p><button type="button" id="cookie-ok" aria-label="Aceptar uso de cookies técnicas">OK</button>';
    document.body.appendChild(c);
    let scrolled=false;
    const hideBanner=()=>{if(!scrolled){scrolled=true;c.style.opacity='0';setTimeout(()=>{c.style.display='none'},300)}};
    window.addEventListener('scroll',hideBanner,{passive:true,once:true});
    const okBtn=document.getElementById('cookie-ok');
    if(okBtn){okBtn.addEventListener('click',()=>{localStorage.setItem('galaxia_cookies_ok','1');c.style.opacity='0';setTimeout(()=>c.remove(),300)})};
  }
});
