document.addEventListener("DOMContentLoaded",()=>{
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
    if(empty)empty.hidden=visible!==0;
  };
  search?.addEventListener("input",apply);
  filter?.addEventListener("change",apply);
  apply();
});
