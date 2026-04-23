# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - maschera i dati personali prima che arrivino a Claude" width="100%">
</p>

**Installazione in una riga. Maschera i dati personali prima che arrivino a Claude.**

> 📖 **Guida completa sul blog:** [OpenAI Privacy Filter: il modello open-source gratuito che maschera i dati personali offline (GPU e CPU)](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)

> 🟨 **Preferisci JavaScript / Node.js?** Stesso tool, versione JS pura (niente Python, niente venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool pseudonimizza ogni prompt che invii a **Claude Code CLI** e ogni richiesta fatta da **Claude Desktop**. Nomi, email, telefoni, indirizzi, IBAN, API key e date vengono sostituiti con placeholder come `[PRIVATE_PERSON_1]` prima di lasciare il tuo computer. I valori originali restano in locale in `~/.claude/privacy-tool/mappings/`.

Basato su [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5B parametri). Gira 100% offline su CPU o GPU.

Leggi in altre lingue: [English](README.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## Esempio reale

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool esempio reale in Claude Code - nome sostituito con placeholder" width="100%">
</p>

Il nome "Pasquale Pillitteri" viene sostituito con `[PRIVATE_PERSON_1]` prima che il prompt raggiunga Claude. La risposta torna con il valore reale grazie al de-sanitize locale.

## Installazione (una riga)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

Tutto qui. L'installer:
1. Crea un venv Python isolato in `~/.claude/privacy-tool/venv`
2. Scarica il modello (~3 GB, una tantum)
3. Registra gli hook in Claude Code (`settings.json`)
4. Registra un server MCP in Claude Desktop (`claude_desktop_config.json`)
5. Esegue uno smoke test

**Requisiti:** Python 3.10+, ~3 GB liberi. GPU opzionale (velocità x10).

## Uso

### Claude Code CLI
Avvia `claude` come al solito. Ogni prompt viene auto-pseudonimizzato. Le risposte vengono ripristinate con i valori originali prima di essere mostrate a te.

```bash
claude
> Scrivi una risposta al mio cliente Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Controlla il log:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Riavvia Claude Desktop. Compaiono 4 tool sotto il server MCP `claude-privacy-tool`:

| Tool | Cosa fa |
|------|---------|
| `privacy_sanitize(text, session_id)` | Sostituisce i PII con placeholder |
| `privacy_desanitize(text, mapping_id, session_id)` | Ripristina i valori reali |
| `privacy_list_sessions()` | Elenca le sessioni salvate |
| `privacy_purge_session(session_id)` | Diritto all'oblio GDPR |

Esempio dentro Claude Desktop:
> Sanitizza questo testo con `privacy_sanitize`, session_id "causa_2026_bianchi":
> "Mario Rossi, nato il 04/05/1982 a Palermo, si rivolge allo studio per…"

Claude ti restituisce la versione mascherata, ci lavora sopra, e tu richiami `privacy_desanitize` quando ti servono i nomi reali.

## Cosa viene mascherato

Otto categorie PII di OpenAI Privacy Filter:

- `private_person` — nomi e cognomi
- `private_address` — indirizzi postali
- `private_email` — email
- `private_phone` — telefoni
- `private_url` — URL con identificatori personali
- `private_date` — date di nascita / sensibili
- `account_number` — IBAN, codici fiscali, P.IVA
- `secret` — password, API key, token

## Disinstallazione

```bash
~/.claude/privacy-tool/uninstall.sh
```

Rimuove hook, server MCP, venv e cache modello. I mapping restano finché non confermi la cancellazione.

## Come funziona

```
  tu ──prompt con dati reali──► hook ──testo sanitizzato──► Claude
                                 │
                       mapping salvato in locale
                                 │
  tu ◄──risposta ripristinata── hook ◄──placeholder── Claude
```

Tutta la pseudonimizzazione avviene in locale. Anthropic vede solo placeholder. Il dizionario placeholder → valore reale vive in `~/.claude/privacy-tool/mappings/` con permessi `0600`.

## A chi serve

- **Avvocati** per redigere atti senza esporre nomi dei clienti (segreto professionale)
- **Medici** per referti senza esporre dati del paziente (segreto medico)
- **DPO e responsabili compliance** per interrogare Claude senza violare GDPR
- **Sviluppatori** per debuggare codice senza incollare API key reali
- **Consulenti, CTU, commercialisti** che trattano dati personali di terzi

## Limitazioni

- È pseudonimizzazione, non anonimizzazione. Chi ha il mapping può re-identificare. Proteggi `~/.claude/privacy-tool/mappings/` con cifratura disco (FileVault, LUKS, BitLocker).
- Non sostituisce la policy review o la DPIA.
- Latenza CPU 1-3 secondi per prompt. GPU 100-300 ms.

## Licenza

MIT

## Autore

Pasquale Pillitteri — [pasqualepillitteri.it](https://pasqualepillitteri.it)

Articolo di riferimento: [Guida OpenAI Privacy Filter](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)
