# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - masquez les données personnelles avant qu'elles n'atteignent Claude" width="100%">
</p>

**Installation en une ligne. Masque les données personnelles avant qu'elles n'arrivent à Claude.**

> 📖 **Guide complet sur le blog:** [OpenAI Privacy Filter : le modèle open-source gratuit qui masque les données personnelles hors ligne (GPU et CPU)](https://pasqualepillitteri.it/fr/news/1352/openai-privacy-filter-masquage-donnees-offline-gpu-cpu)

> 🟨 **Vous préférez JavaScript / Node.js ?** Même outil, portage JS pur (pas de Python, pas de venv) : [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool pseudonymise chaque prompt que vous envoyez à **Claude Code CLI** et chaque requête effectuée par **Claude Desktop**. Noms, emails, téléphones, adresses, IBAN, clés API et dates sont remplacés par des placeholders comme `[PRIVATE_PERSON_1]` avant de quitter votre ordinateur. Les valeurs originales restent en local dans `~/.claude/privacy-tool/mappings/`.

Basé sur [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5B paramètres). Fonctionne 100% hors ligne sur CPU ou GPU.

Read in other languages: [English](README.md) · [Italiano](README.it.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## Exemple réel

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool exemple réel dans Claude Code - nom remplacé par un placeholder" width="100%">
</p>

Le nom "Pasquale Pillitteri" est remplacé par `[PRIVATE_PERSON_1]` avant que le prompt n'atteigne Claude. La réponse revient avec la valeur réelle grâce à la désanonymisation locale.

## Installation (une ligne)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

C'est tout. L'installeur :
1. Crée un venv Python isolé dans `~/.claude/privacy-tool/venv`
2. Télécharge le modèle (~3 Go, une seule fois)
3. Enregistre les hooks dans Claude Code (`settings.json`)
4. Enregistre un serveur MCP dans Claude Desktop (`claude_desktop_config.json`)
5. Exécute un smoke test

**Prérequis :** Python 3.10+, ~3 Go libres. GPU optionnel (vitesse x10).

## Utilisation

### Claude Code CLI
Lancez `claude` comme d'habitude. Chaque prompt est auto-pseudonymisé. Les réponses sont restaurées avec les valeurs originales avant de vous être présentées.

```bash
claude
> Écris une réponse à mon client Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Consultez le log :
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Redémarrez Claude Desktop. 4 outils apparaissent sous le serveur MCP `claude-privacy-tool` :

| Outil | Ce qu'il fait |
|-------|---------------|
| `privacy_sanitize(text, session_id)` | Remplace les PII par des placeholders |
| `privacy_desanitize(text, mapping_id, session_id)` | Restaure les valeurs réelles |
| `privacy_list_sessions()` | Liste les sessions sauvegardées |
| `privacy_purge_session(session_id)` | Droit à l'oubli GDPR |

Exemple dans Claude Desktop :
> Sanitise ce texte avec `privacy_sanitize`, session_id "affaire_2026_bianchi" :
> "Mario Rossi, né le 04/05/1982 à Palerme, s'adresse au cabinet pour…"

Claude vous retourne la version masquée, travaille dessus, et vous rappelez `privacy_desanitize` quand vous avez besoin des noms réels.

## Ce qui est masqué

Huit catégories PII d'OpenAI Privacy Filter :

- `private_person` — noms et prénoms
- `private_address` — adresses postales
- `private_email` — emails
- `private_phone` — téléphones
- `private_url` — URL avec identifiants personnels
- `private_date` — dates de naissance / sensibles
- `account_number` — IBAN, codes fiscaux, numéros TVA
- `secret` — mots de passe, clés API, tokens

## Désinstallation

```bash
~/.claude/privacy-tool/uninstall.sh
```

Supprime hooks, serveur MCP, venv et cache du modèle. Les mappings restent jusqu'à ce que vous confirmiez leur suppression.

## Comment ça marche

```
  vous ──prompt avec données réelles──► hook ──texte sanitisé──► Claude
                                         │
                              mapping sauvegardé en local
                                         │
  vous ◄──réponse restaurée── hook ◄──placeholder── Claude
```

Toute la pseudonymisation se déroule en local. Anthropic ne voit que des placeholders. Le dictionnaire placeholder vers valeur réelle réside dans `~/.claude/privacy-tool/mappings/` avec permissions `0600`.

## À qui ça sert

- **Avocats** pour rédiger des actes sans exposer les noms des clients (secret professionnel)
- **Médecins** pour des comptes-rendus sans exposer les données du patient (secret médical)
- **DPO et responsables conformité** pour interroger Claude sans violer le GDPR
- **Développeurs** pour déboguer du code sans coller de vraies clés API
- **Consultants, experts judiciaires, comptables** qui traitent des données personnelles de tiers

## Limitations

- C'est de la pseudonymisation, pas de l'anonymisation. Quiconque possède le mapping peut ré-identifier. Protégez `~/.claude/privacy-tool/mappings/` avec un chiffrement de disque (FileVault, LUKS, BitLocker).
- Ne remplace pas la revue de politique ou la DPIA.
- Latence CPU 1-3 secondes par prompt. GPU 100-300 ms.

## Licence

MIT

## Auteur

Pasquale Pillitteri, [pasqualepillitteri.it](https://pasqualepillitteri.it)

Article de référence : [Guide OpenAI Privacy Filter](https://pasqualepillitteri.it/fr/news/1352/openai-privacy-filter-masquage-donnees-offline-gpu-cpu)
