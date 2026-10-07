# Razítkovač

Malý lokální nástroj, který do PDF vloží schvalovací razítko jako v Adobe. Nahrajete PDF, kliknete do náhledu na místo, kam má razítko přijít, a stáhnete hotový soubor `<původní_název>_approved.pdf`.

Razítko má tvar zeleného zaobleného obdélníku s textem **SCHVÁLENO** a pod ním `Jméno, 16:28, 7. 10. 2026` (čas razítkování v zóně Europe/Prague).

## Vlastnosti

- Drag & drop (nebo výběr souboru), náhled všech stránek pod sebou.
- Klik do stránky umístí razítko (střed razítka do místa kliku), dalším kliknutím ho přesunete. Před kliknutím je u kurzoru jeho náhled.
- Správné umístění i na otočených stránkách, na stránkách různé velikosti a s CropBoxem jiným než MediaBox. Razítko nepřeteče přes okraj.
- Razítko je průhledné PNG ve vysokém rozlišení, takže vypadá stejně v každé čtečce; diakritika funguje (font DejaVu Sans Bold Oblique ve složce `fonts/`).
- Jméno na razítku zadáte při prvním spuštění, uloží se jen ve vašem prohlížeči a jde kdykoli resetovat.
- Soukromí: server běží jen na `127.0.0.1`, soubory se drží pouze v paměti a po stažení se zahodí.
- Chybové stavy: soubor, který není PDF, poškozené nebo šifrované PDF, příliš velký soubor.

## Spuštění

### Windows – jedním souborem

Dvojklik na `Razitkovac.bat`. Při prvním spuštění si sám vytvoří virtuální prostředí a nainstaluje závislosti, pak otevře prohlížeč. Vyžaduje Python 3.11+.

### Ručně

1. Vytvořte virtuální prostředí:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
   ```
2. Nainstalujte závislosti:
   ```
   pip install -r requirements.txt
   ```
3. Spusťte:
   ```
   python app.py
   ```
   Otevře se http://127.0.0.1:5000.

## Použití

1. Při prvním spuštění zadejte své jméno (změníte ho tlačítkem „Reset jména“ v záhlaví).
2. Přetáhněte PDF do okna nebo klikněte a vyberte soubor.
3. Klikněte na místo pro razítko (dalším kliknutím ho přesunete) a dejte „Razítkovat a stáhnout“.

## Nastavení

V [config.py](config.py): časová zóna, port, limit velikosti souboru (výchozí 50 MB) a číslo verze.

## Struktura

| Soubor | Účel |
| --- | --- |
| `app.py` | Flask server a routy |
| `pdf_ops.py` | render stránek, převod souřadnic, vložení razítka (PyMuPDF) |
| `stamp.py` | vzhled razítka a čas (Pillow) |
| `templates/index.html` | celé rozhraní (jeden HTML soubor, vanilla JS) |
| `fonts/` | font razítka a jeho licence |

## Technologie

Python, Flask, PyMuPDF, Pillow. Frontend bez frameworků a buildu.

Vyvinul Petr Skřivánek s pomocí Claude Code.
