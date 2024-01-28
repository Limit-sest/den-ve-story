<img src="./repo_assets/Cover img.png" alt="Cover image" style="height: 400px; border-radius: 1.5rem;"/>

# Dnes je... v Instagram Story
> Program který každý den postne story obsahující den a svátek.

Používám [instauto](https://github.com/stanvanrooy/instauto) pro nahrání story, [Pillow](https://github.com/python-pillow/Pillow) pro generování obrázku a k získání svátků a dat používám [svátky API](https://svatkyapi.cz/).
## Jak začít?
Je to jednoduché. Nejprve je potřeba si stáhnout kód a pak různé knihovny
```
git clone https://github.com/Limit-sest/den-v-biu
```
```
pip install -r requirements.txt
```
Program funguje tak že zkombinuje 2 obrázky - Pozadí a 1 náhodný z `/assets/bg2`.

Doporučuju změnit obrázek pozadí v `/assets/bg.png`, otestováno s rozlišením 720x1280.

Když se zapne program, zeptá se na heslo a username. Je zde i možnost si údaje uložit, ale **budou uloženy v nezabezpečeném souboru ⚠️**

A teď by všechno (snad) mělo fungovat!

---
Nezaručuju že to nezablokuje daný účet, všechno je na vlastní nebezpečí!
