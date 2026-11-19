# pacifico-auto.com — sitio web

Sitio estático (HTML + CSS + JS), bilingüe EN/ES. Pensado para publicarse en GitHub Pages y conectar el dominio de GoDaddy.
Contenido sacado del knowledge graph (`notas/organizaciones/Pacífico Auto.md` y notas relacionadas).
Sin datos privados de clientes. El formulario no guarda nada: abre WhatsApp con el mensaje listo.

## Páginas de autos
`build.py` lee las fichas en `../pacifico-auto/autos/<auto>/` (ficha.md + fotos/) y genera `autos/index.html` y una página por auto.
- `python3 build.py` — solo autos reales.
- `python3 build.py --ejemplo` — incluye el auto de muestra (lleva una franja roja de "MUESTRA" y no entra a Git).
Las fotos se convierten a JPG de máximo 1600 px. El botón "Reservar" abre WhatsApp con el mensaje listo.
