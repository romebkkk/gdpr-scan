#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  GDPR SCAN  ·  Informational cookie & privacy compliance scanner
  by DataFlow Elegance
=============================================================================
Enter a URL and get an audit of how the site handles cookies and privacy
BEFORE the visitor gives consent — the core of GDPR / ePrivacy compliance.

It does NOT give legal advice. It's an informational checklist + score that
helps you (or your clients) spot the obvious problems and fix them.
=============================================================================
"""
import argparse
import datetime
import json
import sys
import urllib.parse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[!] Falta Playwright. Instala:  pip install -r requirements.txt")
    print("                                python -m playwright install chromium")
    sys.exit(1)

# UTF-8 en consola Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BRAND = "DataFlow Elegance"
BRAND_URL = "https://dataflowelegance.es"
VERSION = "1.0.0"

# --- Firmas de trackers de terceros (subcadenas en las URLs de red) ---------
TRACKERS = {
    "Google Analytics": ["google-analytics.com", "/gtag/js", "/analytics.js", "/collect?v="],
    "Google Tag Manager": ["googletagmanager.com"],
    "Meta / Facebook Pixel": ["connect.facebook.net", "facebook.com/tr"],
    "Google Ads / DoubleClick": ["doubleclick.net", "googleadservices.com", "googlesyndication.com"],
    "Hotjar": ["static.hotjar.com", "script.hotjar.com"],
    "Microsoft Clarity": ["clarity.ms"],
    "TikTok Pixel": ["analytics.tiktok.com"],
    "LinkedIn Insight": ["snap.licdn.com", "px.ads.linkedin.com"],
    "Twitter / X Pixel": ["static.ads-twitter.com", "t.co/i/adsct"],
    "Pinterest Tag": ["ct.pinterest.com"],
}

# --- Plataformas de gestión de consentimiento (CMP) conocidas ---------------
CMPS = {
    "Cookiebot": ["cookiebot.com", "consent.cookiebot"],
    "OneTrust": ["onetrust.com", "cookielaw.org"],
    "Complianz": ["complianz"],
    "Didomi": ["didomi.io"],
    "Osano": ["osano.com"],
    "CookieYes": ["cookieyes.com", "cookie-law-info"],
    "Iubenda": ["iubenda.com"],
    "Termly": ["termly.io"],
    "Usercentrics": ["usercentrics"],
    "Quantcast Choice": ["quantcast.mgr.consensu", "choice.consensu"],
}

# Cookies de primera parte que no penalizamos (técnicas / de consentimiento)
ESSENTIAL_HINTS = [
    "csrf", "xsrf", "session", "sess", "phpsessid", "wordpress_", "wp-settings",
    "wp_", "woocommerce_", "cookie_consent", "cookieconsent", "cookielawinfo",
    "__cf", "cf_", "consent", "borlabs", "complianz",
]


def norm_url(u):
    if not urllib.parse.urlparse(u).scheme:
        u = "https://" + u
    return u


def _classify(haystacks, sigmap):
    found = []
    for name, sigs in sigmap.items():
        for h in haystacks:
            if any(s in h for s in sigs):
                found.append(name)
                break
    return sorted(found)


def scan(url, timeout_ms=30000):
    """Carga la web SIN consentir nada y observa qué hace."""
    url = norm_url(url)
    requests_seen = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36")
        )
        page = context.new_page()
        page.on("request", lambda r: requests_seen.append(r.url))

        status = None
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            status = resp.status if resp else None
        except Exception:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                status = resp.status if resp else None
            except Exception as e:
                browser.close()
                raise RuntimeError(f"No se pudo cargar la web: {e}")

        page.wait_for_timeout(2500)  # dejar que salten trackers tardíos
        cookies = context.cookies()
        html = page.content()
        try:
            links = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => ((e.getAttribute('href')||'') + ' ' + (e.innerText||'')))",
            )
        except Exception:
            links = []
        final_url = page.url
        browser.close()

    # --- Análisis --------------------------------------------------------
    low_html = html.lower()
    link_blob = " ".join(links).lower()
    non_essential = [c for c in cookies
                     if not any(h in c["name"].lower() for h in ESSENTIAL_HINTS)]

    return {
        "url": url,
        "final_url": final_url,
        "http_status": status,
        "scanned_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "https": final_url.startswith("https://"),
        "cookies_total": len(cookies),
        "non_essential_cookies_before_consent": sorted(c["name"] for c in non_essential),
        "cookies_without_secure_flag": sorted(c["name"] for c in cookies if not c.get("secure")),
        "trackers": _classify(requests_seen, TRACKERS),
        "cmp_detected": _classify(requests_seen + [low_html], CMPS),
        "cookie_banner_hint": any(h in low_html for h in [
            "aceptar cookies", "gestionar cookies", "consentimiento", "política de cookies",
            "cookie policy", "we use cookies", "usamos cookies", "rgpd", "gdpr", "consent",
        ]),
        "privacy_policy_link": any(k in link_blob for k in [
            "privacidad", "privacy", "aviso legal", "datenschutz"]),
        "cookie_policy_link": "cookie" in link_blob,
    }


def evaluate(r):
    """Convierte el escaneo en una lista de comprobaciones ponderadas + score."""
    checks = []

    def add(label, status, weight, detail, tip=""):
        checks.append({"label": label, "status": status, "weight": weight,
                       "detail": detail, "tip": tip})

    # 1) Cookies no esenciales ANTES de consentir (lo más grave)
    nec = r["non_essential_cookies_before_consent"]
    if nec:
        add("Cookies no esenciales antes del consentimiento", "fail", 30,
            f"Se instalaron {len(nec)} cookie(s) sin consentimiento: {', '.join(nec[:8])}"
            + ("…" if len(nec) > 8 else ""),
            "El RGPD/ePrivacy exige consentimiento PREVIO. No cargues cookies no técnicas hasta que el usuario acepte.")
    else:
        add("Cookies no esenciales antes del consentimiento", "pass", 30,
            "No se detectaron cookies no esenciales antes de consentir. 👌")

    # 2) Trackers de terceros disparados antes de consentir
    if r["trackers"]:
        add("Trackers de terceros antes del consentimiento", "fail", 25,
            "Se dispararon antes de consentir: " + ", ".join(r["trackers"]),
            "Carga GA, Meta Pixel, etc. SOLO tras el consentimiento (Consent Mode / bloqueo previo).")
    else:
        add("Trackers de terceros antes del consentimiento", "pass", 25,
            "No se detectaron trackers de terceros antes de consentir. 👌")

    # 3) Banner / CMP de cookies
    if r["cmp_detected"]:
        add("Banner de consentimiento de cookies", "pass", 15,
            "CMP detectada: " + ", ".join(r["cmp_detected"]))
    elif r["cookie_banner_hint"]:
        add("Banner de consentimiento de cookies", "warn", 15,
            "Se detectan indicios de banner, pero ninguna CMP conocida.",
            "Verifica que el banner permita RECHAZAR tan fácil como aceptar.")
    else:
        add("Banner de consentimiento de cookies", "fail", 15,
            "No se detectó ningún banner de cookies.",
            "Añade un banner que pida consentimiento antes de cargar cookies no técnicas.")

    # 4) HTTPS
    add("Conexión segura (HTTPS)", "pass" if r["https"] else "fail", 15,
        "La web usa HTTPS." if r["https"] else "La web NO usa HTTPS.",
        "" if r["https"] else "Instala un certificado SSL y fuerza redirección a HTTPS.")

    # 5) Enlace a política de privacidad
    add("Enlace a Política de Privacidad", "pass" if r["privacy_policy_link"] else "fail", 10,
        "Se encontró enlace a privacidad / aviso legal." if r["privacy_policy_link"]
        else "No se encontró enlace visible a política de privacidad.",
        "" if r["privacy_policy_link"] else "Añade en el pie un enlace claro a tu Política de Privacidad.")

    # 6) Enlace a política de cookies
    add("Enlace a Política de Cookies", "pass" if r["cookie_policy_link"] else "warn", 5,
        "Se encontró enlace relacionado con cookies." if r["cookie_policy_link"]
        else "No se encontró un enlace claro a la política de cookies.",
        "" if r["cookie_policy_link"] else "Publica una Política de Cookies y enlázala desde el banner.")

    score = 0.0
    for c in checks:
        if c["status"] == "pass":
            score += c["weight"]
        elif c["status"] == "warn":
            score += c["weight"] * 0.5
    score = round(score)

    grade = ("A" if score >= 90 else "B" if score >= 75 else
             "C" if score >= 60 else "D" if score >= 40 else "F")
    return checks, score, grade


# --- Salida por consola -----------------------------------------------------
_ICON = {"pass": "✅", "warn": "⚠️ ", "fail": "❌"}


def print_report(r, checks, score, grade):
    print("\n" + "=" * 70)
    print(f"  🛡️  GDPR SCAN v{VERSION}  ·  {BRAND}")
    print("=" * 70)
    print(f"  URL      : {r['final_url']}")
    print(f"  Fecha    : {r['scanned_at']}")
    print(f"  PUNTUACIÓN: {score}/100   (Nota: {grade})")
    print("=" * 70)
    for c in checks:
        print(f"  {_ICON[c['status']]} {c['label']}")
        print(f"      {c['detail']}")
        if c["tip"] and c["status"] != "pass":
            print(f"      💡 {c['tip']}")
    print("=" * 70)
    print(f"  Informe informativo — no constituye asesoramiento legal.")
    print(f"  {BRAND} · {BRAND_URL}")
    print("=" * 70 + "\n")


# --- Informe HTML con marca de agua ----------------------------------------
def html_report(r, checks, score, grade):
    color = ("#16a34a" if grade in ("A", "B") else
             "#d97706" if grade == "C" else "#dc2626")
    rows = ""
    badge = {"pass": ("#16a34a", "OK"), "warn": ("#d97706", "AVISO"), "fail": ("#dc2626", "FALLO")}
    for c in checks:
        col, txt = badge[c["status"]]
        tip = f'<div class="tip">💡 {c["tip"]}</div>' if (c["tip"] and c["status"] != "pass") else ""
        rows += f"""<tr>
          <td><span class="pill" style="background:{col}">{txt}</span></td>
          <td><strong>{c['label']}</strong><div class="detail">{c['detail']}</div>{tip}</td>
        </tr>"""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GDPR Scan · {r['final_url']}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
          margin:0; background:#0b0f17; color:#e5e7eb; }}
  .wrap {{ max-width:820px; margin:0 auto; padding:32px 20px 80px; position:relative; z-index:1; }}
  .watermark {{ position:fixed; inset:0; display:flex; align-items:center; justify-content:center;
                pointer-events:none; z-index:0; opacity:.05; transform:rotate(-24deg);
                font-size:6vw; font-weight:800; letter-spacing:.1em; white-space:nowrap; }}
  h1 {{ font-size:1.4rem; margin:0 0 4px; }}
  .sub {{ color:#9ca3af; font-size:.9rem; margin-bottom:24px; word-break:break-all; }}
  .score {{ display:flex; align-items:center; gap:16px; background:#111827; border:1px solid #1f2937;
            border-radius:16px; padding:20px 24px; margin-bottom:24px; }}
  .grade {{ font-size:3rem; font-weight:800; color:{color}; line-height:1; }}
  .num {{ font-size:1.1rem; color:#9ca3af; }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:14px 8px; border-bottom:1px solid #1f2937; vertical-align:top; }}
  .pill {{ color:#fff; font-size:.72rem; font-weight:700; padding:3px 8px; border-radius:999px; }}
  .detail {{ color:#9ca3af; font-size:.88rem; margin-top:4px; }}
  .tip {{ color:#93c5fd; font-size:.85rem; margin-top:6px; }}
  footer {{ margin-top:32px; color:#6b7280; font-size:.8rem; text-align:center; }}
  a {{ color:#93c5fd; }}
</style></head>
<body>
  <div class="watermark">{BRAND}</div>
  <div class="wrap">
    <h1>🛡️ GDPR Scan — Informe de cumplimiento</h1>
    <div class="sub">{r['final_url']} · {r['scanned_at']}</div>
    <div class="score">
      <div class="grade">{grade}</div>
      <div><div class="num">Puntuación</div><div style="font-size:1.6rem;font-weight:700">{score}/100</div></div>
    </div>
    <table>{rows}</table>
    <footer>
      Informe <strong>informativo</strong> — no constituye asesoramiento legal.<br>
      Generado con <strong>GDPR Scan</strong> · <a href="{BRAND_URL}">{BRAND}</a>
    </footer>
  </div>
</body></html>"""


def main():
    ap = argparse.ArgumentParser(description=f"GDPR Scan v{VERSION} — {BRAND}")
    ap.add_argument("url", help="URL de la web a analizar (ej: ejemplo.com)")
    ap.add_argument("--json", action="store_true", help="Imprime el resultado en JSON")
    ap.add_argument("--out", metavar="FICHERO.html", help="Guarda un informe HTML")
    ap.add_argument("--timeout", type=int, default=30000, help="Timeout de carga en ms")
    args = ap.parse_args()

    try:
        r = scan(args.url, timeout_ms=args.timeout)
    except RuntimeError as e:
        print(f"[!] {e}")
        sys.exit(2)

    checks, score, grade = evaluate(r)

    if args.json:
        print(json.dumps({"scan": r, "checks": checks, "score": score, "grade": grade},
                         ensure_ascii=False, indent=2))
    else:
        print_report(r, checks, score, grade)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(html_report(r, checks, score, grade))
        print(f"[✓] Informe HTML guardado en: {args.out}")


if __name__ == "__main__":
    main()
