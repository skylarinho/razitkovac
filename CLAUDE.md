# Razítkovač – konvence

- Malý lokální nástroj (Flask + PyMuPDF + Pillow, frontend = jeden HTML + vanilla JS). Žádné frameworky, build ani databáze; nepřidávat funkce navíc (jen razítko APPROVED).
- Kód a komentáře anglicky, UI i razítko pouze česky (bez přepínače jazyků). Texty rozhraní jsou ve slovníku `TEXTS` v index.html; server vrací jen chybové kódy (`code`), hlášky skládá frontend. Text a formát data razítka jsou ve stamp.py.
- Jméno na razítku ukládá prohlížeč (localStorage), server dostává jméno v každém požadavku (`name`); v configu žádné jméno není.
- Server jen na 127.0.0.1; dokumenty jen v paměti (`DOCS` v app.py), po razítkování se mažou.
- Nastavení serveru (časová zóna, port, limity) patří do config.py.
- Moduly: `app.py` routy, `pdf_ops.py` práce s PDF (render, souřadnice, vložení), `stamp.py` vzhled razítka a čas.
- Souřadnice: klient posílá polohu jako podíl šířky/výšky zobrazené stránky; pdf_ops převádí do PDF bodů přes `derotation_matrix` a ořezává, aby razítko nepřetékalo. Při vkládání se `/Rotate` dočasně nuluje (obchází chybu PyMuPDF u otočených stránek s posunutým CropBoxem) – nemazat.
- Razítko je PNG z Pillow (4× supersampling) s fontem `fonts/DejaVuSans-BoldOblique.ttf`; ne standardní PDF fonty (diakritika).
- Po změně souřadnic nebo razítka otestovat na PDF s rotací 90/180/270, různými velikostmi stránek a CropBoxem ≠ MediaBox.
- Spuštění: `python app.py` ve venv.
