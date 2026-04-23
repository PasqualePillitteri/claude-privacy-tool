# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - enmascara los datos personales antes de que lleguen a Claude" width="100%">
</p>

**Instalación en una línea. Enmascara los datos personales antes de que lleguen a Claude.**

> 📖 **Guía completa en el blog:** [OpenAI Privacy Filter: el modelo open-source gratuito que enmascara datos personales offline (GPU y CPU)](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)

> 🟨 **¿Prefieres JavaScript / Node.js?** Misma herramienta, versión JS pura (sin Python, sin venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool seudonimiza cada prompt que envías a **Claude Code CLI** y cada solicitud realizada por **Claude Desktop**. Nombres, correos, teléfonos, direcciones, IBAN, claves API y fechas se sustituyen por marcadores como `[PRIVATE_PERSON_1]` antes de salir de tu ordenador. Los valores originales permanecen en local en `~/.claude/privacy-tool/mappings/`.

Basado en [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5B parámetros). Funciona 100% offline en CPU o GPU.

Léelo en otros idiomas: [English](README.md) · [Italiano](README.it.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---

## Instalación (una línea)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

Eso es todo. El instalador:
1. Crea un venv Python aislado en `~/.claude/privacy-tool/venv`
2. Descarga el modelo (~3 GB, una sola vez)
3. Registra los hooks en Claude Code (`settings.json`)
4. Registra un servidor MCP en Claude Desktop (`claude_desktop_config.json`)
5. Ejecuta un smoke test

**Requisitos:** Python 3.10+, ~3 GB libres. GPU opcional (velocidad x10).

## Uso

### Claude Code CLI
Inicia `claude` como de costumbre. Cada prompt se seudonimiza automáticamente. Las respuestas se restauran con los valores originales antes de mostrártelas.

```bash
claude
> Escribe una respuesta a mi cliente Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Consulta el log:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Reinicia Claude Desktop. Aparecen 4 herramientas bajo el servidor MCP `claude-privacy-tool`:

| Herramienta | Qué hace |
|-------------|----------|
| `privacy_sanitize(text, session_id)` | Sustituye los PII por marcadores |
| `privacy_desanitize(text, mapping_id, session_id)` | Restaura los valores reales |
| `privacy_list_sessions()` | Enumera las sesiones guardadas |
| `privacy_purge_session(session_id)` | Derecho al olvido GDPR |

Ejemplo dentro de Claude Desktop:
> Sanitiza este texto con `privacy_sanitize`, session_id "causa_2026_bianchi":
> "Mario Rossi, nacido el 04/05/1982 en Palermo, se dirige al despacho para…"

Claude te devuelve la versión enmascarada, trabaja sobre ella, y tú invocas `privacy_desanitize` cuando necesitas los nombres reales.

## Qué se enmascara

Ocho categorías PII de OpenAI Privacy Filter:

- `private_person` nombres y apellidos
- `private_address` direcciones postales
- `private_email` correos electrónicos
- `private_phone` teléfonos
- `private_url` URL con identificadores personales
- `private_date` fechas de nacimiento / sensibles
- `account_number` IBAN, códigos fiscales, NIF/CIF
- `secret` contraseñas, claves API, tokens

## Desinstalación

```bash
~/.claude/privacy-tool/uninstall.sh
```

Elimina hooks, servidor MCP, venv y caché del modelo. Los mappings permanecen hasta que confirmes la eliminación.

## Cómo funciona

```
  tú ──prompt con datos reales──► hook ──texto sanitizado──► Claude
                                   │
                         mapping guardado en local
                                   │
  tú ◄──respuesta restaurada── hook ◄──marcador── Claude
```

Toda la seudonimización ocurre en local. Anthropic ve solo marcadores. El diccionario marcador → valor real vive en `~/.claude/privacy-tool/mappings/` con permisos `0600`.

## A quién sirve

- **Abogados** para redactar escritos sin exponer nombres de los clientes (secreto profesional)
- **Médicos** para informes sin exponer datos del paciente (secreto médico)
- **DPO y responsables de compliance** para consultar a Claude sin vulnerar el GDPR
- **Desarrolladores** para depurar código sin pegar claves API reales
- **Consultores, peritos judiciales, asesores fiscales** que tratan datos personales de terceros

## Limitaciones

- Es seudonimización, no anonimización. Quien tenga el mapping puede reidentificar. Protege `~/.claude/privacy-tool/mappings/` con cifrado de disco (FileVault, LUKS, BitLocker).
- No sustituye la revisión de políticas ni la DPIA.
- Latencia CPU 1-3 segundos por prompt. GPU 100-300 ms.

## Licencia

MIT

## Autor

Pasquale Pillitteri [pasqualepillitteri.it](https://pasqualepillitteri.it)

Artículo de referencia: [Guía OpenAI Privacy Filter](https://pasqualepillitteri.it/news/1350/openai-privacy-filter-pii-masking-offline-gpu-cpu)
