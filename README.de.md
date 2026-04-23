# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - personenbezogene Daten maskieren, bevor sie Claude erreichen" width="100%">
</p>

**Installation in einer Zeile. Maskiert personenbezogene Daten, bevor sie Claude erreichen.**

> 📖 **Vollständige Anleitung im Blog:** [OpenAI Privacy Filter: das kostenlose Open-Source-Modell, das personenbezogene Daten offline maskiert (GPU und CPU)](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)

> 🟨 **Bevorzugen Sie JavaScript / Node.js?** Dasselbe Tool, reine JS-Portierung (kein Python, kein venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool pseudonymisiert jeden Prompt, den du an **Claude Code CLI** sendest, und jede Anfrage von **Claude Desktop**. Namen, E-Mails, Telefonnummern, Adressen, IBAN, API-Keys und Daten werden durch Platzhalter wie `[PRIVATE_PERSON_1]` ersetzt, bevor sie deinen Computer verlassen. Die Originalwerte bleiben lokal in `~/.claude/privacy-tool/mappings/`.

Basiert auf [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5 Mrd. Parameter). Läuft zu 100% offline auf CPU oder GPU.

In anderen Sprachen lesen: [English](README.md) · [Italiano](README.it.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---

## Installation (eine Zeile)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

Das war's. Der Installer:
1. Erstellt ein isoliertes Python-venv in `~/.claude/privacy-tool/venv`
2. Lädt das Modell herunter (~3 GB, einmalig)
3. Registriert die Hooks in Claude Code (`settings.json`)
4. Registriert einen MCP-Server in Claude Desktop (`claude_desktop_config.json`)
5. Führt einen Smoke-Test aus

**Voraussetzungen:** Python 3.10+, ~3 GB freier Speicher. GPU optional (10-fache Geschwindigkeit).

## Verwendung

### Claude Code CLI
Starte `claude` wie gewohnt. Jeder Prompt wird automatisch pseudonymisiert. Die Antworten werden mit den Originalwerten wiederhergestellt, bevor sie dir angezeigt werden.

```bash
claude
> Schreibe eine Antwort an meinen Kunden Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Protokoll überprüfen:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Starte Claude Desktop neu. Es erscheinen 4 Tools unter dem MCP-Server `claude-privacy-tool`:

| Tool | Funktion |
|------|---------|
| `privacy_sanitize(text, session_id)` | Ersetzt PII durch Platzhalter |
| `privacy_desanitize(text, mapping_id, session_id)` | Stellt die echten Werte wieder her |
| `privacy_list_sessions()` | Listet gespeicherte Sitzungen auf |
| `privacy_purge_session(session_id)` | Recht auf Vergessenwerden nach DSGVO |

Beispiel innerhalb von Claude Desktop:
> Bereinige diesen Text mit `privacy_sanitize`, session_id "causa_2026_bianchi":
> "Mario Rossi, geboren am 04.05.1982 in Palermo, wendet sich an die Kanzlei, um…"

Claude gibt dir die maskierte Version zurück, arbeitet damit, und du rufst `privacy_desanitize` auf, wenn du die echten Namen brauchst.

## Was maskiert wird

Acht PII-Kategorien von OpenAI Privacy Filter:

- `private_person` — Vor- und Nachnamen
- `private_address` — Postanschriften
- `private_email` — E-Mails
- `private_phone` — Telefonnummern
- `private_url` — URLs mit persönlichen Kennungen
- `private_date` — Geburtsdaten / sensible Daten
- `account_number` — IBAN, Steuernummer, USt-IdNr.
- `secret` — Passwörter, API-Keys, Tokens

## Deinstallation

```bash
~/.claude/privacy-tool/uninstall.sh
```

Entfernt Hooks, MCP-Server, venv und Modell-Cache. Die Mappings bleiben erhalten, bis du die Löschung bestätigst.

## So funktioniert es

```
  du ──Prompt mit echten Daten──► Hook ──bereinigter Text──► Claude
                                 │
                       Mapping lokal gespeichert
                                 │
  du ◄──wiederhergestellte Antwort── Hook ◄──Platzhalter── Claude
```

Die gesamte Pseudonymisierung erfolgt lokal. Anthropic sieht nur Platzhalter. Das Wörterbuch Platzhalter → echter Wert liegt in `~/.claude/privacy-tool/mappings/` mit Berechtigungen `0600`.

## Für wen es nützlich ist

- **Anwälte** zum Verfassen von Schriftsätzen, ohne Mandantennamen preiszugeben (Berufsgeheimnis)
- **Ärzte** für Befunde, ohne Patientendaten offenzulegen (ärztliche Schweigepflicht)
- **DSB und Compliance-Verantwortliche**, um Claude zu befragen, ohne die DSGVO zu verletzen
- **Entwickler**, um Code zu debuggen, ohne echte API-Keys einzufügen
- **Berater, Sachverständige, Steuerberater**, die personenbezogene Daten Dritter verarbeiten

## Einschränkungen

- Es handelt sich um Pseudonymisierung, nicht Anonymisierung. Wer das Mapping besitzt, kann re-identifizieren. Schütze `~/.claude/privacy-tool/mappings/` mit Festplattenverschlüsselung (FileVault, LUKS, BitLocker).
- Ersetzt keine Policy-Prüfung oder DSFA.
- Latenz CPU 1-3 Sekunden pro Prompt. GPU 100-300 ms.

## Lizenz

MIT

## Autor

Pasquale Pillitteri, [pasqualepillitteri.it](https://pasqualepillitteri.it)

Referenzartikel: [Leitfaden OpenAI Privacy Filter](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)
