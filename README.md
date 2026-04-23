# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - mask personal data before it reaches Claude" width="100%">
</p>

**One-line installer. Mask personal data before it reaches Claude.**

> 📖 **Full guide on the blog:** [OpenAI Privacy Filter: the free open-source model that masks personal data offline (GPU and CPU)](https://pasqualepillitteri.it/en/news/1351/openai-privacy-filter-pii-masking-offline-gpu-cpu)

> 📦 **Dedicated article for this tool:** [Claude Privacy Tool: the free tool that masks personal data before it reaches Claude (Python + JavaScript)](https://pasqualepillitteri.it/en/news/1361/claude-privacy-tool-hook-privacy-claude-code-desktop)

> 🟨 **Prefer JavaScript / Node.js?** Same tool, pure JS port (no Python, no venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool pseudonymizes every prompt you send to **Claude Code CLI** and every request made from **Claude Desktop**. Names, emails, phone numbers, addresses, IBANs, API keys and dates are replaced with placeholders like `[PRIVATE_PERSON_1]` before leaving your machine. The original values stay local, encrypted in `~/.claude/privacy-tool/mappings/`.

Powered by [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1.5B params). Runs 100% offline on CPU or GPU.

Read in your language: [Italiano](README.it.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## Real example

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool real example in Claude Code - name replaced with placeholder" width="100%">
</p>

The name "Pasquale Pillitteri" is replaced by `[PRIVATE_PERSON_1]` before the prompt reaches Claude. The response comes back with the real value thanks to local de-sanitization.

## Install (one line)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

That is it. The installer:
1. Creates an isolated Python venv in `~/.claude/privacy-tool/venv`
2. Downloads the model (~3 GB, one time)
3. Registers hooks in Claude Code (`settings.json`)
4. Registers an MCP server in Claude Desktop (`claude_desktop_config.json`)
5. Runs a smoke test

**Requirements:** Python 3.10+, ~3 GB free disk. GPU optional (10x speedup).

## Use

### Claude Code CLI
Just run `claude` as usual. Every prompt is auto-pseudonymized. Responses are restored to the original values before being shown to you.

```bash
claude
> Draft a reply to my client Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Check the log:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Restart Claude Desktop. Four tools become available under the `claude-privacy-tool` MCP server:

| Tool | What it does |
|------|--------------|
| `privacy_sanitize(text, session_id)` | Replace PII with placeholders |
| `privacy_desanitize(text, mapping_id, session_id)` | Restore real values |
| `privacy_list_sessions()` | List stored sessions |
| `privacy_purge_session(session_id)` | GDPR right-to-erasure |

Example inside Claude Desktop:
> Sanitize this with `privacy_sanitize`, session_id "case_2026_bianchi":
> "Mario Rossi, born 04/05/1982 in Palermo, asks the firm to…"

Claude returns the masked version, works on it, and you call `privacy_desanitize` when you need the real names back.

## What gets masked

Eight PII categories from OpenAI Privacy Filter:

- `private_person` — names and surnames
- `private_address` — postal addresses
- `private_email` — emails
- `private_phone` — phone numbers
- `private_url` — URLs carrying identifiers
- `private_date` — dates of birth / sensitive
- `account_number` — IBAN, fiscal codes, VAT numbers
- `secret` — passwords, API keys, tokens

## Uninstall

```bash
~/.claude/privacy-tool/uninstall.sh
```

Removes hooks, MCP server registration, venv and model cache. Mappings are kept unless you confirm deletion.

## How it works

```
  you ──prompt with real data──► hook ──sanitized──► Claude
                                  │
                        mapping stored locally
                                  │
  you ◄──restored response──── hook ◄──placeholders── Claude
```

All pseudonymization is local. Anthropic only ever sees placeholders. The mapping from placeholders to real values lives in `~/.claude/privacy-tool/mappings/` with file permissions `0600`.

## Who is it for

- **Lawyers** drafting briefs without exposing client names under professional secrecy
- **Doctors** preparing referrals without leaking patient data under medical secrecy
- **DPOs and compliance officers** showing GDPR-safe prompts to Claude
- **Developers** debugging code without pasting real API keys
- **Consultants, CTUs, accountants** dealing with third-party personal data

## Limitations

- This is pseudonymization, not anonymization. Anyone with the mapping can re-identify. Protect `~/.claude/privacy-tool/mappings/` with disk encryption (FileVault, LUKS, BitLocker).
- Not a substitute for policy review or DPIA.
- CPU latency 1-3 seconds per prompt. GPU brings it to 100-300 ms.

## License

MIT

## Author

Pasquale Pillitteri — [pasqualepillitteri.it](https://pasqualepillitteri.it)

Reference article: [OpenAI Privacy Filter guide](https://pasqualepillitteri.it/en/news/1351/openai-privacy-filter-pii-masking-offline-gpu-cpu)
