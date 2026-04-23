# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - 在个人数据到达 Claude 之前对其进行屏蔽" width="100%">
</p>

**一行命令安装. 在数据发送到 Claude 之前对其进行脱敏.**

> 📖 **博客完整指南:** [OpenAI Privacy Filter: 免费开源模型，可离线屏蔽个人数据 (GPU 和 CPU)](https://pasqualepillitteri.it/zh/news/1357/openai-privacy-filter-pingbi-geren-shuju-offline-gpu-cpu)

> 📦 **此工具的专题文章:** [Claude Privacy Tool: 在 Claude 之前屏蔽个人数据的免费工具 (Python + JavaScript)](https://pasqualepillitteri.it/zh/news/1367/claude-privacy-tool-hook-privacy-claude-code-desktop)

> 🟨 **更喜欢 JavaScript / Node.js?** 相同的工具, 纯 JS 移植 (无 Python, 无 venv): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool 会对你发送给 **Claude Code CLI** 的每个提示词以及 **Claude Desktop** 发出的每个请求进行假名化处理. 姓名, 邮箱, 电话, 地址, IBAN, API key 和日期会在离开你的电脑之前被替换为 `[PRIVATE_PERSON_1]` 之类的占位符. 原始值保留在本地 `~/.claude/privacy-tool/mappings/` 目录下.

基于 [OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 15 亿参数). 在 CPU 或 GPU 上 100% 离线运行.

用其他语言阅读: [English](README.md) · [Italiano](README.it.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## 真实示例

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool 在 Claude Code 中的真实示例 - 姓名被替换为占位符" width="100%">
</p>

姓名 "Pasquale Pillitteri" 在 prompt 到达 Claude 之前被替换为 `[PRIVATE_PERSON_1]`。由于本地反假名化, 响应返回时带有真实值。

## 安装 (一行命令)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

就这样. 安装脚本会:
1. 在 `~/.claude/privacy-tool/venv` 创建独立的 Python venv
2. 下载模型 (约 3 GB, 一次性)
3. 在 Claude Code 中注册 hook (`settings.json`)
4. 在 Claude Desktop 中注册 MCP 服务器 (`claude_desktop_config.json`)
5. 执行一次冒烟测试

**要求:** Python 3.10+, 约 3 GB 可用空间. GPU 可选 (速度提升 10 倍).

## 使用

### Claude Code CLI
照常启动 `claude`. 每个提示词会自动假名化. 响应在展示给你之前会用原始值进行还原.

```bash
claude
> Scrivi una risposta al mio cliente Mario Rossi (mario@example.com, IBAN IT60X0542...)
```

查看日志:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
重启 Claude Desktop. 在 MCP 服务器 `claude-privacy-tool` 下会出现 4 个工具:

| 工具 | 作用 |
|------|---------|
| `privacy_sanitize(text, session_id)` | 用占位符替换 PII |
| `privacy_desanitize(text, mapping_id, session_id)` | 还原真实值 |
| `privacy_list_sessions()` | 列出已保存的会话 |
| `privacy_purge_session(session_id)` | GDPR 被遗忘权 |

在 Claude Desktop 中的示例:
> 用 `privacy_sanitize` 对这段文本进行脱敏, session_id 为 "causa_2026_bianchi":
> "Mario Rossi, nato il 04/05/1982 a Palermo, si rivolge allo studio per…"

Claude 会返回脱敏后的版本并在其上工作, 当你需要真实姓名时再调用 `privacy_desanitize`.

## 会被遮蔽的内容

OpenAI Privacy Filter 的八类 PII:

- `private_person` 姓名和姓氏
- `private_address` 邮政地址
- `private_email` 邮箱
- `private_phone` 电话
- `private_url` 含个人标识符的 URL
- `private_date` 出生日期或敏感日期
- `account_number` IBAN, 税号, 增值税号
- `secret` 密码, API key, token

## 卸载

```bash
~/.claude/privacy-tool/uninstall.sh
```

移除 hook, MCP 服务器, venv 和模型缓存. 映射会保留, 直到你确认删除.

## 工作原理

```
  tu ──prompt con dati reali──► hook ──testo sanitizzato──► Claude
                                 │
                       mapping salvato in locale
                                 │
  tu ◄──risposta ripristinata── hook ◄──placeholder── Claude
```

所有假名化过程都在本地完成. Anthropic 只看到占位符. 占位符到真实值的字典保存在 `~/.claude/privacy-tool/mappings/`, 权限为 `0600`.

## 适用人群

- **律师** 起草文书时不暴露客户姓名 (职业保密)
- **医生** 撰写报告时不暴露患者数据 (医疗保密)
- **DPO 和合规负责人** 在不违反 GDPR 的前提下询问 Claude
- **开发者** 调试代码时无需粘贴真实 API key
- **顾问, 法庭技术顾问, 会计师** 处理第三方个人数据

## 限制

- 这是假名化, 不是匿名化. 持有映射的人可以重新识别身份. 请用磁盘加密 (FileVault, LUKS, BitLocker) 保护 `~/.claude/privacy-tool/mappings/`.
- 不能替代 policy review 或 DPIA.
- CPU 延迟每条提示词 1 至 3 秒. GPU 为 100 至 300 毫秒.

## 许可证

MIT

## 作者

Pasquale Pillitteri [pasqualepillitteri.it](https://pasqualepillitteri.it)

参考文章: [Guida OpenAI Privacy Filter](https://pasqualepillitteri.it/zh/news/1357/openai-privacy-filter-pingbi-geren-shuju-offline-gpu-cpu)
