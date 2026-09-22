# 🛡️ GDPR Scan

> Enter a URL and get an instant audit of how a website handles **cookies and privacy — *before* the visitor consents**, which is exactly where GDPR / ePrivacy is broken most often. Score, findings, and fix-it tips. Console + branded HTML report.

**No account. No API keys. Runs locally. It never claims to be legal advice — it's an informational checklist that catches the obvious problems.**

<sub>[🇪🇸 Versión en español más abajo](#-español)</sub>

---

## ✨ What it checks

| Check | Why it matters |
|-------|----------------|
| 🍪 **Non-essential cookies set *before* consent** | The #1 GDPR/ePrivacy violation — no cookies until the user accepts |
| 📡 **Third-party trackers firing before consent** | Google Analytics, Meta Pixel, GTM, Hotjar, TikTok, LinkedIn… |
| ✅ **Cookie consent banner / CMP** | Detects Cookiebot, OneTrust, Complianz, Didomi, CookieYes… |
| 🔒 **HTTPS** | Secure transport |
| 📄 **Privacy Policy link** | Legally required, must be reachable |
| 📄 **Cookie Policy link** | Should be linked from the banner |

Output: a **0–100 score + grade (A–F)**, every finding explained, and a concrete tip to fix each problem.

## ⚙️ How it works

`GDPR Scan` opens the page in a **headless Chromium** (Playwright) as a fresh visitor who has **not consented to anything**, records every network request and cookie, and analyses what fired before consent. That's the honest way to test GDPR/ePrivacy: what happens *before* the user clicks "Accept".

## 🚀 Quick start

```bash
pip install -r requirements.txt
python -m playwright install chromium

# Scan a site
python gdpr_scan.py example.com

# Save a branded HTML report
python gdpr_scan.py example.com --out report.html

# Machine-readable output
python gdpr_scan.py example.com --json
```

| Flag | Description |
|------|-------------|
| `--out report.html` | Save a shareable HTML report (with watermark) |
| `--json` | Print structured JSON (for pipelines / integrations) |
| `--timeout 30000` | Page load timeout in ms |

## 🌐 Web UI (localhost)

Prefer a visual interface? Launch the local web app:

```bash
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Then open **http://localhost:8000**, type a URL and get a live, shareable compliance report — score, findings and fix-it tips, all in the browser.

## ⚖️ Disclaimer

`GDPR Scan` is an **informational tool**, not legal advice and not a certification. GDPR/ePrivacy compliance depends on your specific data processing, legal basis and documentation. Use the results as a **starting checklist** and consult a professional for a formal assessment. Scans only load the public page as a normal visitor would.

## 📄 License

[MIT](LICENSE) © 2026 DataFlow Elegance

---

## 🇪🇸 Español

**GDPR Scan** audita una web en segundos: metes una URL y te dice cómo trata las **cookies y la privacidad *antes* de que el usuario dé su consentimiento** — que es justo donde más se incumple el RGPD / ePrivacy. Puntuación, hallazgos y consejos para arreglarlo. Informe por consola y en HTML con marca de agua.

**Qué comprueba:**
- 🍪 **Cookies no esenciales instaladas ANTES de consentir** (la infracción nº1 del RGPD).
- 📡 **Trackers de terceros disparados antes del consentimiento** (Google Analytics, Meta Pixel, GTM, Hotjar, TikTok, LinkedIn…).
- ✅ **Banner / CMP de cookies** (Cookiebot, OneTrust, Complianz, Didomi, CookieYes…).
- 🔒 **HTTPS**, 📄 **enlace a Política de Privacidad** y 📄 **de Cookies**.
- → **Puntuación 0–100 + nota (A–F)** con explicación y consejo para cada punto.

### Uso rápido

```bash
pip install -r requirements.txt
python -m playwright install chromium

python gdpr_scan.py tuweb.com                 # escaneo por consola
python gdpr_scan.py tuweb.com --out informe.html   # informe HTML con marca de agua
python gdpr_scan.py tuweb.com --json          # salida JSON
```

### Aviso legal

`GDPR Scan` es una herramienta **informativa**, no asesoramiento legal ni una certificación. El cumplimiento del RGPD depende de tu tratamiento de datos concreto, tu base legal y tu documentación. Usa los resultados como **checklist inicial** y consulta con un profesional para una evaluación formal.

---

<div align="center">
Hecho con ❤️ por <a href="https://github.com/romebkkk">DataFlow Elegance</a> · <a href="https://dataflowelegance.es">dataflowelegance.es</a>
</div>
