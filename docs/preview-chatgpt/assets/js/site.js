document.addEventListener("DOMContentLoaded",()=>{
  const nav=document.querySelector(".nav-links");
  const actions=document.querySelector(".nav-actions");
  const isFrench=document.documentElement.lang.toLowerCase().startsWith("fr");
  if(nav){
    const brand=document.querySelector(".brand");
    const programmeHref=brand?new URL("programme/",brand.href).href:null;
    if(programmeHref&&!Array.from(nav.querySelectorAll("a")).some(a=>/programme/i.test(a.textContent)||/programme\\//i.test(a.href))){
      const link=document.createElement("a");
      link.href=programmeHref;
      link.textContent="Programme";
      nav.insertBefore(link,nav.firstChild);
    }
  }
  if(actions&&!actions.querySelector("[data-theme-toggle]")){
    const theme=document.createElement("button");
    theme.type="button";
    theme.className="theme-toggle";
    theme.setAttribute("data-theme-toggle","");
    theme.setAttribute("aria-label",isFrench?"Changer de thème":"Switch theme");
    theme.title=isFrench?"Changer de thème":"Switch theme";
    theme.innerHTML='<svg class="ico-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg><svg class="ico-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
    const lang=actions.querySelector(".lang");
    actions.insertBefore(theme,lang||null);
  }
  const toggle=document.querySelector(".menu-toggle");
  const nav=document.querySelector(".nav-links");
  if(toggle&&nav){
    const isFrench=document.documentElement.lang.toLowerCase().startsWith("fr");
    const openLabel=isFrench?"Ouvrir le menu":"Open menu";
    const closeLabel=isFrench?"Fermer le menu":"Close menu";
    const setOpen=(open,returnFocus=false)=>{
      nav.classList.toggle("is-open",open);
      toggle.setAttribute("aria-expanded",String(open));
      toggle.setAttribute("aria-label",open?closeLabel:openLabel);
      if(!open&&returnFocus)toggle.focus();
    };
    toggle.addEventListener("click",()=>setOpen(!nav.classList.contains("is-open")));
    document.addEventListener("keydown",event=>{
      if(event.key==="Escape"&&nav.classList.contains("is-open"))setOpen(false,true);
    });
    document.addEventListener("click",event=>{
      if(nav.classList.contains("is-open")&&!nav.contains(event.target)&&!toggle.contains(event.target))setOpen(false);
    });
    nav.addEventListener("click",event=>{
      if(event.target.closest("a"))setOpen(false);
    });
    window.addEventListener("resize",()=>{
      if(window.matchMedia("(min-width: 851px)").matches)setOpen(false);
    });
  }
  const search=document.querySelector("[data-search]");
  const filter=document.querySelector("[data-filter]");
  const cards=[...document.querySelectorAll("[data-lesson]")];
  const empty=document.querySelector("[data-empty]");
  const sections=[...document.querySelectorAll("[data-module-section]")];
  const isFrenchLib=document.documentElement.lang.toLowerCase().startsWith("fr");
  const lessonWord=isFrenchLib?"leçon":"lesson";
  const lessonsWord=isFrenchLib?"leçons":"lessons";
  const apply=()=>{
    const q=(search?.value||"").trim().toLocaleLowerCase();
    const f=filter?.value||"all";
    let visible=0;
    cards.forEach(card=>{
      const text=(card.textContent+" "+(card.dataset.keywords||"")).toLocaleLowerCase();
      const category=card.dataset.category||"all";
      card.hidden=!(text.includes(q)&&(f==="all"||f===category));
      if(!card.hidden)visible++;
    });
    sections.forEach(sec=>{
      const kept=[...sec.querySelectorAll("[data-lesson]")].filter(c=>!c.hidden).length;
      sec.hidden=kept===0;
      const counter=sec.querySelector("[data-visible-count]");
      if(counter)counter.textContent=kept+" "+(kept===1?lessonWord:lessonsWord);
    });
    if(empty)empty.hidden=visible!==0;
  };
  search?.addEventListener("input",apply);
  filter?.addEventListener("change",apply);
  apply();
});

/* ---- Thème clair/sombre (ACTU-BASICS premium) ---------------------------
 * Le thème initial est posé AVANT la première peinture par un script inline
 * du <head> qui lit `localStorage.getItem("ab-theme")`. Ici on se contente
 * de câbler la bascule : clic ↔ data-theme ↔ localStorage.
 */
document.addEventListener("DOMContentLoaded",()=>{
  const btns=document.querySelectorAll("[data-theme-toggle]");
  if(!btns.length)return;
  const html=document.documentElement;
  try{
    const saved=localStorage.getItem("ab-theme");
    if(saved==="dark"||saved==="light")html.setAttribute("data-theme",saved);
  }catch(e){}
  const getCurrent=()=>{
    const explicit=html.getAttribute("data-theme");
    if(explicit==="dark"||explicit==="light")return explicit;
    return matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";
  };
  const apply=(t)=>{
    html.setAttribute("data-theme",t);
    try{localStorage.setItem("ab-theme",t);}catch(e){}
    const metaTheme=document.querySelector('meta[name="theme-color"]');
    if(metaTheme)metaTheme.setAttribute("content",t==="dark"?"#0f1619":"#f8f6ef");
  };
  btns.forEach(b=>{
    b.addEventListener("click",()=>apply(getCurrent()==="dark"?"light":"dark"));
  });
});

/* ---- Table des matières sticky sur les pages leçons ---------------------
 * Alimentée par les <h2> de .lesson-content. Indique la section active
 * pendant le défilement. Pas de polyfill : IntersectionObserver suffit.
 */
document.addEventListener("DOMContentLoaded",()=>{
  const content=document.querySelector(".lesson-content");
  if(!content)return;
  let nav=document.querySelector("[data-lesson-toc]");
  const headings=content.querySelectorAll("h2");
  if(!nav&&headings.length>2){
    const layout=content.closest(".lesson-layout");
    if(layout){
      nav=document.createElement("aside");
      nav.className="lesson-aside";
      nav.setAttribute("data-lesson-toc","");
      nav.setAttribute("aria-label",document.documentElement.lang.toLowerCase().startsWith("fr")?"Sommaire":"Contents");
      const title=document.createElement("h3");
      title.textContent=document.documentElement.lang.toLowerCase().startsWith("fr")?"Dans cette leçon":"In this lesson";
      nav.appendChild(title);
      layout.appendChild(nav);
    }
  }
  if(!nav)return;
  const hero=document.querySelector(".page-hero .container");
  const intro=hero?.querySelector("p");
  if(intro&&!hero.querySelector(".lesson-reading-meta")){
    const words=(content.textContent||"").trim().split(/\\s+/).filter(Boolean).length;
    const minutes=Math.max(1,Math.ceil(words/220));
    const meta=document.createElement("p");
    meta.className="lesson-reading-meta";
    meta.textContent=document.documentElement.lang.toLowerCase().startsWith("fr")?"Lecture · "+minutes+" min":"Reading time · "+minutes+" min";
    intro.insertAdjacentElement("afterend",meta);
  }
  if(!headings.length){nav.remove();return;}
  const list=document.createElement("ol");
  list.className="lesson-toc-list";
  const links=new Map();
  headings.forEach((h,i)=>{
    if(!h.id)h.id="s-"+(i+1)+"-"+(h.textContent||"").toLowerCase().replace(/[^\w]+/g,"-").slice(0,40);
    const li=document.createElement("li");
    const a=document.createElement("a");
    a.href="#"+h.id;
    a.textContent=h.textContent;
    li.appendChild(a);
    list.appendChild(li);
    links.set(h.id,a);
  });
  nav.appendChild(list);
  const io=new IntersectionObserver((entries)=>{
    const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
    if(visible.length){
      links.forEach(a=>a.classList.remove("is-active"));
      const active=links.get(visible[0].target.id);
      if(active)active.classList.add("is-active");
    }
  },{rootMargin:"-30% 0px -60% 0px",threshold:0});
  headings.forEach(h=>io.observe(h));
});
