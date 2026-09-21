# Sauce Demo – Regressions-Testsuite

Automatisierte Regressionstests für den Webshop [saucedemo.com](https://www.saucedemo.com/),
umgesetzt mit **Python**, **Playwright** und **pytest**. Nach jedem Lauf entsteht ein
HTML-Report inklusive Screenshots der fehlgeschlagenen Tests.

**97 Testfälle** in neun Testdateien, alle gegen die laufende Anwendung verifiziert.

---

## Inhalt

- [Schnellstart](#schnellstart)
- [Tests ausführen](#tests-ausführen)
- [HTML-Report](#html-report)
- [Testabdeckung](#testabdeckung)
- [Projektstruktur](#projektstruktur)
- [Designentscheidungen](#designentscheidungen)
- [Bekannte Defekte der Anwendung](#bekannte-defekte-der-anwendung)
- [Abweichungen von der Anforderung](#abweichungen-von-der-anforderung)

---

## Schnellstart

Voraussetzung: **Python 3.10 oder neuer**.

```bash
git clone <REPOSITORY-URL>
cd testplaywright

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install chromium

pytest
```

Der vollständige Lauf dauert rund vier Minuten.

---

## Tests ausführen

| Zweck | Befehl |
|---|---|
| Kompletter Regressionslauf | `pytest` |
| Sichtbarer Browser | `pytest --headed` |
| Verlangsamt zum Mitschauen | `pytest --headed --slowmo 500` |
| Anderer Browser | `pytest --browser firefox` (auch `webkit`) |
| Einzelne Datei | `pytest tests/test_checkout.py` |
| Einzelner Test | `pytest tests/test_login.py::test_logout_ends_session` |
| Nur die dokumentierten Defekte | `pytest -m known_issue` |
| Parallel (4 Prozesse) | `pytest -n 4` |

Beim Debuggen lohnt sich der sequenzielle Lauf: parallel vermischen sich die Ausgaben
der vier Prozesse und werden unlesbar.

---

## HTML-Report

Der Report wird bei jedem Lauf automatisch erzeugt:

```
reports/report.html
```

Die Datei ist mit `--self-contained-html` erstellt, enthält also alle Styles und Bilder
und lässt sich direkt weitergeben.

```bash
start reports\report.html      # Windows
open reports/report.html       # macOS
xdg-open reports/report.html   # Linux
```

Bei einem Fehlschlag enthält der Report zusätzlich einen **eingebetteten Screenshot**
des Fehlerzeitpunkts und die **URL**, auf der der Test gescheitert ist. **Video** und
**Playwright-Trace** liegen unter `reports/artifacts/`.

Den Trace kann man Schritt für Schritt nachspielen:

```bash
python -m playwright show-trace reports/artifacts/<test-ordner>/trace.zip
```

---

## Testabdeckung

**Anmeldung und Zugriffsschutz** (`tests/test_login.py`)
- Anmeldung mit `standard_user`, Anmeldung per Enter-Taste
- alle fünf nicht gesperrten Demo-Benutzer können sich anmelden
- gesperrter Benutzer wird mit der korrekten Meldung abgewiesen
- falsches Passwort, unbekannter Benutzer, leerer Benutzername, leeres Passwort
- Fehlermeldung ist schließbar, Eingabefelder werden als fehlerhaft markiert
- Passwortfeld ist maskiert
- geschützte Seiten sind ohne Session nicht direkt aufrufbar
- Abmelden beendet die Session tatsächlich (Prüfung per erneutem Direktaufruf)
- der Zurück-Button stellt nach dem Abmelden keinen Zugriff wieder her

**Produktübersicht** (`tests/test_inventory.py`)
- alle sechs Artikel mit Name, Beschreibung, Preis und Bild
- Preise stimmen mit den hinterlegten Referenzdaten überein
- Warenkorb-Zähler erscheint erst mit dem ersten Artikel und zählt korrekt hoch
- Button wechselt zwischen „Add to cart" und „Remove"
- Zähler verschwindet wieder, wenn der letzte Artikel entfernt wird
- Warenkorbinhalt übersteht ein Neuladen der Seite

**Sortierung** (`tests/test_sorting.py`)
- Standardsortierung ist Name A–Z
- Name A–Z, Name Z–A, Preis aufsteigend, Preis absteigend
- die Artikelanzahl bleibt nach jeder Sortierung unverändert

**Produktdetailseite** (`tests/test_product_detail.py`)
- jede der sechs Detailseiten zeigt die zugehörigen Daten
- Hinzufügen und Entfernen funktioniert auch von der Detailseite
- „Back to products" führt in den Katalog zurück
- der Warenkorb-Zustand ist zwischen Detailseite und Katalog konsistent

**Warenkorb** (`tests/test_cart.py`)
- hinzugefügte Artikel erscheinen mit Menge und Preis
- Artikel lassen sich entfernen, der Zähler folgt
- „Continue Shopping" behält den Warenkorb
- „Checkout" öffnet Schritt 1

**Bestellprozess** (`tests/test_checkout.py`)
- Pflichtfeldprüfung für Vorname, Nachname und PLZ
- Abbrechen in Schritt 1 führt in den Warenkorb, in Schritt 2 in den Katalog
- die Zusammenfassung listet die Artikel samt Zahlungs- und Versandinformationen
- **Rechenprüfung**: Zwischensumme = Summe der Artikelpreise, Steuer = 8 %,
  Gesamtsumme = Zwischensumme + Steuer
- der Abschluss zeigt die Bestätigung und leert den Warenkorb
- „Generate PDF order" liefert eine gültige, nicht leere PDF-Datei

**Navigation und Fußzeile** (`tests/test_navigation.py`)
- Burger-Menü öffnet und schließt
- alle fünf Menüeinträge sind vorhanden
- „All Items", „About", „Reset App State"
- die Fußzeile verweist auf X, Facebook und LinkedIn und öffnet in einem neuen Tab

**Vollständige Kaufstrecken** (`tests/test_end_to_end.py`)
- kompletter Kauf über Sortierung, Detailseite, Warenkorb, Checkout bis zur Abmeldung
- Artikel mit Sonderzeichen im Namen (`Test.allTheThings() T-Shirt (Red)`)
- Kauf mit `performance_glitch_user` trotz künstlicher Latenz

**Dokumentierte Anwendungsdefekte** (`tests/test_known_issues.py`) – siehe unten.

---

## Projektstruktur

```
testplaywright/
├── conftest.py                # Fixtures und Report-Anbindung
├── pytest.ini                 # Standardoptionen, Marker, Reportpfad
├── requirements.txt
├── .github/workflows/         # GitHub Actions
└── tests/
    ├── test_login.py
    ├── test_inventory.py
    ├── test_sorting.py
    ├── test_product_detail.py
    ├── test_cart.py
    ├── test_checkout.py
    ├── test_navigation.py
    ├── test_end_to_end.py
    └── test_known_issues.py
```

Die `conftest.py` liegt im Wurzelverzeichnis und stellt drei Fixtures bereit:

| Fixture | Zweck |
|---|---|
| `configure_test_id` | setzt einmalig pro Lauf `data-test` als Test-ID-Attribut |
| `login_page` | geöffnete Login-Seite |
| `inventory_page` | angemeldet als `standard_user`, Katalog geladen |

---

## Designentscheidungen

**Web-First-Assertions.** Geprüft wird ausschließlich mit `expect()` aus
`playwright.sync_api`. Diese Prüfungen wiederholen sich automatisch, bis die Bedingung
zutrifft oder das Zeitlimit greift. Dadurch enthält das Projekt **kein einziges
`sleep`** und fast keine manuellen Wartezeilen.

```python
expect(inventory_page.get_by_test_id("inventory-item-name")).to_have_text(NAMES_ASC)
```

Diese eine Zeile prüft Anzahl, Inhalt und Reihenfolge aller sechs Treffer – und wartet
dabei, bis die Neusortierung gerendert ist.

**Locator-Strategie.** Elemente werden bevorzugt so beschrieben, wie ein Nutzer sie
wahrnimmt:

| Priorität | Methode | Verwendet für |
|---|---|---|
| 1 | `get_by_role` | Schaltflächen, das Sortier-Dropdown, das Burger-Menü |
| 2 | `get_by_placeholder` | Formularfelder im Checkout |
| 3 | `get_by_test_id` | Produktkarten, Menüeinträge, Fußzeile, Warenkorb |
| 4 | CSS | nur dort, wo die Anwendung keinen besseren Anker bietet |

Sauce Demo verwendet `data-test` statt des Playwright-Standards `data-testid`. Das wird
einmalig in der `conftest.py` gesetzt:

```python
playwright.selectors.set_test_id_attribute("data-test")
```

Zu beachten ist, dass die Anwendung die Schreibweisen mischt: CSS-Klassen mit
Unterstrichen (`product_sort_container`), `data-test` mit Bindestrichen
(`product-sort-container`), im Checkout-Formular dagegen camelCase (`firstName`).

**Referenzdaten statt Selbstvergleich.** Produktnamen und Preise sind als Konstanten
hinterlegt und werden nicht zur Laufzeit von derselben Seite gelesen. Ein falscher Preis
im Shop würde sonst unbemerkt bleiben.

**Jeder Test ist unabhängig.** Jeder Testfall startet in einem frischen Browser-Kontext,
also ohne Cookies und ohne Session. Die Reihenfolge der Tests ist deshalb irrelevant, und
die Suite lässt sich ohne Anpassung parallel ausführen (`pytest -n 4`).

**Parametrisierung statt Duplikation.** Wiederkehrende Muster – sechs Produkte, fünf
Login-Fehlerfälle, vier Sortieroptionen, fünf geschützte Seiten – sind über
`pytest.mark.parametrize` abgebildet. Jede Variante erscheint als eigener Testfall im
Report, und ein Fehlschlag benennt genau die betroffene Variante.

**Externe Links werden geprüft, nicht besucht.** Die Verweise auf saucelabs.com und die
sozialen Netzwerke werden über ihr `href`-Attribut kontrolliert. Ein Klick würde die
Suite von fremden Servern abhängig machen.

---

## Bekannte Defekte der Anwendung

Sauce Demo enthält absichtlich eingebaute Fehler. Diese sind nicht ausgeklammert, sondern
in `tests/test_known_issues.py` als Testfälle mit dem erwarteten **korrekten** Verhalten
hinterlegt und mit `xfail` markiert. Sie färben den Lauf nicht rot – sobald ein Defekt
behoben wird, meldet pytest ein `XPASS` und weist auf die Änderung hin.

| Betroffen | Defekt |
|---|---|
| `problem_user` | alle Artikel zeigen dasselbe Bild |
| `problem_user` | Sortierung wirkt nicht |
| `problem_user` | Feld „Last Name" im Checkout nicht befüllbar |
| `error_user` | Sortierung meldet „Sorting is broken! This error has been reported to Backtrace." |
| `error_user` | „Finish" wirft `cesetRart is not a function` (verdrehtes `resetCart`), es erfolgt keine Navigation zur Bestätigung |
| alle Benutzer | der Checkout lässt sich mit leerem Warenkorb starten |

Ein Test in dieser Datei ist **nicht** als `xfail` markiert: Er fängt über
`page.on("pageerror", ...)` den JavaScript-Fehler ab und dokumentiert damit die Ursache
des fehlschlagenden Checkouts statt nur das Symptom.

Zwei häufig genannte Defekte ließen sich **nicht** reproduzieren und sind deshalb nicht
dokumentiert: `error_user` kann das Feld „Last Name" befüllen und Artikel aus dem
Warenkorb entfernen.

Die fachlichen Tests laufen bewusst mit `standard_user`, damit Defekte der Anwendung
nicht mit Defekten der Testsuite vermischt werden.
