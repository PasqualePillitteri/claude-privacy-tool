# Claude Privacy Tool

<p align="center">
  <img src="claude-privacy-tool.png" alt="Claude Privacy Tool - kişisel verileri Claude'a ulaşmadan önce maskeler" width="100%">
</p>

**Tek satırda kurulum. Kişisel verileri Claude'a ulaşmadan önce maskeler.**

> 📖 **Blogda tam kılavuz:** [OpenAI Privacy Filter: kişisel verileri çevrimdışı maskeleyen ücretsiz açık kaynak model (GPU ve CPU)](https://pasqualepillitteri.it/tr/news/1355/openai-privacy-filter-kisisel-veri-maskeleme-offline-gpu-cpu)

> 🟨 **JavaScript / Node.js mı tercih ediyorsunuz?** Aynı araç, saf JS port (Python yok, venv yok): [claude-privacy-tool-js](https://github.com/pasqualepillitteri/claude-privacy-tool-js)

Claude Privacy Tool, **Claude Code CLI**'ye gönderdiğiniz her istemi ve **Claude Desktop** tarafından yapılan her isteği takma adla korur. İsimler, e-postalar, telefonlar, adresler, IBAN'lar, API anahtarları ve tarihler, bilgisayarınızdan ayrılmadan önce `[PRIVATE_PERSON_1]` gibi yer tutucularla değiştirilir. Orijinal değerler yerel olarak `~/.claude/privacy-tool/mappings/` içinde kalır.

[OpenAI Privacy Filter](https://huggingface.co/openai/privacy-filter) (Apache 2.0, 1,5B parametre) üzerine kuruludur. CPU veya GPU üzerinde %100 çevrimdışı çalışır.

Diğer dillerde oku: [English](README.md) · [Italiano](README.it.md) · [Français](README.fr.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [中文](README.zh.md) · [Português](README.pt.md) · [日本語](README.ja.md)

---


## Gerçek örnek

<p align="center">
  <img src="claude-privacy-tool-example.png" alt="Claude Privacy Tool Claude Code'da gerçek örnek - ad placeholder ile değiştirildi" width="100%">
</p>

"Pasquale Pillitteri" adı, prompt Claude'a ulaşmadan önce `[PRIVATE_PERSON_1]` ile değiştirilir. Yanıt, yerel desanitize sayesinde gerçek değerle geri döner.

## Kurulum (tek satır)

```bash
curl -sSL https://raw.githubusercontent.com/pasqualepillitteri/claude-privacy-tool/main/install.sh | bash
```

Hepsi bu kadar. Kurulum betiği:
1. `~/.claude/privacy-tool/venv` içinde izole bir Python venv oluşturur
2. Modeli indirir (~3 GB, bir kez)
3. Claude Code'daki kancaları kaydeder (`settings.json`)
4. Claude Desktop'ta bir MCP sunucusu kaydeder (`claude_desktop_config.json`)
5. Bir duman testi çalıştırır

**Gereksinimler:** Python 3.10+, ~3 GB boş alan. GPU isteğe bağlıdır (x10 hız).

## Kullanım

### Claude Code CLI
`claude`'u her zamanki gibi başlatın. Her istem otomatik olarak takma adla korunur. Yanıtlar, size gösterilmeden önce orijinal değerlerle geri yüklenir.

```bash
claude
> Müşterim Mario Rossi'ye (mario@example.com, IBAN IT60X0542...) bir yanıt yaz
```

Logu kontrol edin:
```bash
tail -f ~/.claude/privacy-tool/hook.log
```

### Claude Desktop
Claude Desktop'u yeniden başlatın. `claude-privacy-tool` MCP sunucusu altında 4 araç görünür:

| Araç | Ne yapar |
|------|----------|
| `privacy_sanitize(text, session_id)` | PII'leri yer tutucularla değiştirir |
| `privacy_desanitize(text, mapping_id, session_id)` | Gerçek değerleri geri yükler |
| `privacy_list_sessions()` | Kayıtlı oturumları listeler |
| `privacy_purge_session(session_id)` | GDPR unutulma hakkı |

Claude Desktop içinde örnek:
> Bu metni `privacy_sanitize` ile temizle, session_id "causa_2026_bianchi":
> "Mario Rossi, 04/05/1982 doğumlu, Palermo'da, ofise başvuruyor..."

Claude size maskelenmiş sürümü döndürür, üzerinde çalışır ve gerçek isimlere ihtiyacınız olduğunda `privacy_desanitize`'ı çağırırsınız.

## Neler maskelenir

OpenAI Privacy Filter'ın sekiz PII kategorisi:

- `private_person` ad ve soyadlar
- `private_address` posta adresleri
- `private_email` e-posta adresleri
- `private_phone` telefon numaraları
- `private_url` kişisel tanımlayıcılı URL'ler
- `private_date` doğum tarihleri veya hassas tarihler
- `account_number` IBAN, vergi kodları, KDV numaraları
- `secret` parolalar, API anahtarları, tokenler

## Kaldırma

```bash
~/.claude/privacy-tool/uninstall.sh
```

Kancaları, MCP sunucusunu, venv'i ve model önbelleğini kaldırır. Eşleştirmeler, silme işlemini onaylayana kadar kalır.

## Nasıl çalışır

```
  siz ──gerçek verili istem──► kanca ──temizlenmiş metin──► Claude
                                 │
                       eşleştirme yerelde kayıtlı
                                 │
  siz ◄──geri yüklenen yanıt── kanca ◄──yer tutucu── Claude
```

Tüm takma ad işlemi yerelde gerçekleşir. Anthropic yalnızca yer tutucuları görür. Yer tutucu ile gerçek değer arasındaki sözlük, `~/.claude/privacy-tool/mappings/` içinde `0600` izinleriyle bulunur.

## Kim için faydalı

- **Avukatlar** için müşteri isimlerini ifşa etmeden dilekçe hazırlamak (mesleki sır)
- **Doktorlar** için hasta verilerini ifşa etmeden rapor yazmak (tıbbi sır)
- **DPO ve uyum sorumluları** için GDPR'ı ihlal etmeden Claude'u sorgulamak
- **Geliştiriciler** için gerçek API anahtarlarını yapıştırmadan kodu ayıklamak
- **Danışmanlar, bilirkişiler, mali müşavirler** için üçüncü tarafların kişisel verilerini işlemek

## Sınırlamalar

- Bu takma addır, anonimleştirme değildir. Eşleştirmeye sahip olan kişi yeniden tanımlama yapabilir. `~/.claude/privacy-tool/mappings/` dizinini disk şifrelemesiyle (FileVault, LUKS, BitLocker) koruyun.
- Politika incelemesinin veya DPIA'nın yerini tutmaz.
- CPU gecikmesi istem başına 1-3 saniyedir. GPU 100-300 ms.

## Lisans

MIT

## Yazar

Pasquale Pillitteri [pasqualepillitteri.it](https://pasqualepillitteri.it)

Referans makale: [OpenAI Privacy Filter Rehberi](https://pasqualepillitteri.it/tr/news/1355/openai-privacy-filter-kisisel-veri-maskeleme-offline-gpu-cpu)
