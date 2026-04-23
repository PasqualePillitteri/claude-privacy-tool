# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - маскирует персональные данные до того, как они попадут в Claude" width="100%">
</p>

**Установка в одну строку. Маскирует персональные данные до того, как они попадут в Claude.**

> 📖 **Полное руководство в блоге:** [OpenAI Privacy Filter: бесплатная open-source модель для маскирования персональных данных офлайн (GPU и CPU)](https://pasqualepillitteri.it/ru/news/1356/openai-privacy-filter-maskirovanie-dannykh-offline-gpu-cpu)

> 🟨 **Предпочитаете JavaScript / Node.js?** Тот же инструмент, чистый JS-порт (без Python, без venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool псевдонимизирует каждый запрос, который вы отправляете в **Claude Code CLI**, и каждый запрос, выполняемый **Claude Desktop**. Имена, email, телефоны, адреса, IBAN, API-ключи и даты заменяются плейсхолдерами вроде `[PRIVATE_PERSON_1]` до того, как покинут ваш компьютер. Исходные значения остаются локально в `~/.claude/privacy-tool/mappings/`.

Основан на [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5 млрд параметров). Работает на 100% офлайн на CPU или GPU.

Читайте на других языках: [English](README.md) · [Italiano](README.it.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## Реальный пример

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool реальный пример в Claude Code - имя заменено на placeholder" width="100%">
</p>

Имя "Pasquale Pillitteri" заменяется на `[PRIVATE_PERSON_1]` до того, как промпт попадёт в Claude. Ответ возвращается с реальным значением благодаря локальной десанитизации.

## Установка (одна строка)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

Это всё. Установщик:
1. Создаёт изолированное окружение Python venv в `~/.claude/privacy-tool/venv`
2. Скачивает модель (~3 ГБ, однократно)
3. Регистрирует хуки в Claude Code (`settings.json`)
4. Регистрирует MCP-сервер в Claude Desktop (`claude_desktop_config.json`)
5. Выполняет smoke-тест

**Требования:** Python 3.10+, ~3 ГБ свободного места. GPU опционально (ускорение в 10 раз).

## Использование

### Claude Code CLI
Запускайте `claude` как обычно. Каждый запрос автоматически псевдонимизируется. Ответы восстанавливаются с исходными значениями до того, как будут показаны вам.

```bash
claude
> Scrivi una risposta al mio cliente Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

Проверьте лог:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Перезапустите Claude Desktop. Появляются 4 инструмента под MCP-сервером `claude-privacy-tool`:

| Инструмент | Что делает |
|------|---------|
| `privacy_sanitize(text, session_id)` | Заменяет PII на плейсхолдеры |
| `privacy_desanitize(text, mapping_id, session_id)` | Восстанавливает реальные значения |
| `privacy_list_sessions()` | Выводит список сохранённых сессий |
| `privacy_purge_session(session_id)` | Право на забвение GDPR |

Пример внутри Claude Desktop:
> Санитизируй этот текст с помощью `privacy_sanitize`, session_id "causa_2026_bianchi":
> "Mario Rossi, рождённый 04/05/1982 в Палермо, обращается в адвокатское бюро..."

Claude возвращает вам маскированную версию, работает с ней, а вы вызываете `privacy_desanitize`, когда вам нужны реальные имена.

## Что маскируется

Восемь категорий PII от OpenAI Privacy Filter:

- `private_person` имена и фамилии
- `private_address` почтовые адреса
- `private_email` email
- `private_phone` телефоны
- `private_url` URL с персональными идентификаторами
- `private_date` даты рождения и прочие чувствительные даты
- `account_number` IBAN, налоговые коды, номера НДС
- `secret` пароли, API-ключи, токены

## Удаление

```bash
~/.claude/privacy-tool/uninstall.sh
```

Удаляет хуки, MCP-сервер, venv и кэш модели. Mapping-файлы остаются до тех пор, пока вы не подтвердите их удаление.

## Как это работает

```
  tu ──prompt con dati reali──► hook ──testo sanitizzato──► Claude
                                 │
                       mapping salvato in locale
                                 │
  tu ◄──risposta ripristinata── hook ◄──placeholder── Claude
```

Вся псевдонимизация происходит локально. Anthropic видит только плейсхолдеры. Словарь плейсхолдер → реальное значение хранится в `~/.claude/privacy-tool/mappings/` с правами `0600`.

## Кому это нужно

- **Адвокаты** для составления процессуальных документов без раскрытия имён клиентов (адвокатская тайна)
- **Врачи** для заключений без раскрытия данных пациента (врачебная тайна)
- **DPO и специалисты по compliance** для работы с Claude без нарушения GDPR
- **Разработчики** для отладки кода без вставки реальных API-ключей
- **Консультанты, судебные эксперты, бухгалтеры**, работающие с персональными данными третьих лиц

## Ограничения

- Это псевдонимизация, а не анонимизация. Тот, у кого есть mapping, может выполнить повторную идентификацию. Защищайте `~/.claude/privacy-tool/mappings/` шифрованием диска (FileVault, LUKS, BitLocker).
- Не заменяет policy review или DPIA.
- Задержка на CPU 1-3 секунды на запрос. На GPU 100-300 мс.

## Лицензия

MIT

## Автор

Pasquale Pillitteri [pasqualepillitteri.it](https://pasqualepillitteri.it)

Справочная статья: [Руководство OpenAI Privacy Filter](https://pasqualepillitteri.it/ru/news/1356/openai-privacy-filter-maskirovanie-dannykh-offline-gpu-cpu)
