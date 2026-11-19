# Cómo publicar pacificoautocr.com

Guía paso a paso. Cada paso que sale de esta Mac lo hace Agustín o se hace solo con su sí.

## 0. Antes de publicar (checklist)
- [ ] Revisó el borrador y aprobó los textos.
- [ ] Logo elegido (se trabaja en otro chat) y puesto en `img/`.
- [ ] Las páginas de autos se generaron con `python3 build.py` (sin `--ejemplo`).
- [ ] Nada privado de clientes ni de vendedores en las páginas (nombres, cédulas, teléfonos, placas si no quiere mostrarlas).

## 1. Repositorio en GitHub online — creado 2026-11-19: github.com/agustincorderoc-oss/pacifico-auto-web (público)
1. Entrar a github.com con su cuenta (o crear una con pacificoautocr@gmail.com).
2. **New repository** → nombre `pacifico-auto-web` → Public → sin README (ya existe aquí) → **Create**.
3. En la Terminal, dentro de esta carpeta (lo corre él, porque el push está bloqueado para Claude):

```bash
git remote add origin https://github.com/agustincorderoc-oss/pacifico-auto-web.git
git branch -M main
git push -u origin main
```

## 2. Encender GitHub Pages
En el repositorio → **Settings → Pages** → Source: *Deploy from a branch* → Branch `main`, carpeta `/ (root)` → **Save**.
El archivo `CNAME` ya dice `pacificoautocr.com`, así que GitHub toma el dominio solo.

## 3. DNS en GoDaddy (con su sí)
GoDaddy → **My Products → pacificoautocr.com → DNS → Manage DNS**.

Borrar (o editar) el registro **A** con nombre `@` que trae GoDaddy ("Parked"/"WebsiteBuilder") y dejar estos:

| Tipo  | Nombre | Valor                    | TTL     |
|-------|--------|--------------------------|---------|
| A     | @      | 185.199.108.153          | 1 hora  |
| A     | @      | 185.199.109.153          | 1 hora  |
| A     | @      | 185.199.110.153          | 1 hora  |
| A     | @      | 185.199.111.153          | 1 hora  |
| CNAME | www    | `agustincorderoc-oss.github.io` | 1 hora  |

No tocar los registros **MX** ni **TXT** si existen (son del correo).
Si el sitio está hecho con el Website Builder de GoDaddy, hay que desconectarlo del dominio primero; si no, GoDaddy vuelve a poner su registro A.

## 4. Verificar
- Esperar de 10 minutos a unas horas.
- En **Settings → Pages**, cuando el chequeo de DNS salga en verde, marcar **Enforce HTTPS**.
- Abrir https://pacificoautocr.com y https://www.pacificoautocr.com.

## Para actualizar después
Cambiar archivos aquí → commit → él corre `git push`. La página se actualiza en 1–2 minutos.
