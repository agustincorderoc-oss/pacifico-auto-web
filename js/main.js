(function(){
  var root=document.documentElement, KEY='pa-lang';
  function setLang(l){root.className='lang-'+l;root.lang=l;try{localStorage.setItem(KEY,l)}catch(e){}}
  var saved=null;try{saved=localStorage.getItem(KEY)}catch(e){}
  setLang(saved||((navigator.language||'en').slice(0,2)==='es'?'es':'en'));
  document.querySelector('.lang-toggle').addEventListener('click',function(){setLang(root.lang==='en'?'es':'en')});
  document.getElementById('year').textContent=new Date().getFullYear();
  document.getElementById('wa-form').addEventListener('submit',function(e){
    e.preventDefault();var f=e.target;
    var msg=(root.lang==='es'?'Hola, soy ':'Hi, I\'m ')+f.name.value+'.\n'+
      (root.lang==='es'?'Servicio: ':'Service: ')+f.service.value+'\n'+
      (f.vehicle.value?(root.lang==='es'?'Vehículo/presupuesto: ':'Vehicle/budget: ')+f.vehicle.value+'\n':'')+
      (f.comments.value||'');
    window.open('https://wa.me/50689505551?text='+encodeURIComponent(msg),'_blank','noopener');
  });
})();
