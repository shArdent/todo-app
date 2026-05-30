from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
import html
import urllib.parse
import urllib.request

from vuln import base_page

router = APIRouter()


SAFE_REDIRECTS = {
    "/", "/vuln", "/vuln/sql-injection", "/vuln/xss/reflected",
    "/vuln/xss/stored", "/vuln/ssti", "/vuln/command-injection",
    "/vuln/path-traversal", "/vuln/ssrf", "/vuln/upload",
    "/vuln/idor/profile", "/vuln/crlf", "/vuln/api/secret",
}


@router.get("/vuln/open-redirect")
async def open_redirect(url: str = "/vuln"):
    if url in SAFE_REDIRECTS:
        return RedirectResponse(url=url, status_code=302)
    safe = html.escape(url)
    return base_page("Open Redirect Test", f"""
    <p>URL diterima: <code>{safe}</code></p>
    <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
        ⛔ REDIRECT DIBLOKIR — hanya URL whitelist yang diizinkan
    </p>
    <p>URL yang diizinkan: <code>/, /vuln, /vuln/...</code></p>
    <p>Coba: <code>https://evil.com</code> — WAF harus blokir.</p>
    """)


BLOCKED_HOSTS = {
    "127.0.0.1", "localhost", "0.0.0.0", "::1",
    "169.254.169.254", "metadata.google.internal",
}
BLOCKED_SCHEMES = {"file", "gopher", "dict"}


def is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme in BLOCKED_SCHEMES:
            return False
        if parsed.hostname in BLOCKED_HOSTS:
            return False
        return True
    except Exception:
        return False


@router.get("/vuln/ssrf", response_class=HTMLResponse)
async def ssrf(url: str = ""):
    safe = html.escape(url)
    body = "<p>SSRF test — request hanya diizinkan ke host publik.</p>"
    if url:
        body += f"""<p>URL diterima: <code>{safe}</code></p>"""
        if is_safe_url(url):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read().decode(errors="replace")[:500]
                    body += f"<pre>{html.escape(data)}</pre>"
            except Exception as e:
                body += f"<p>Error: {html.escape(str(e))}</p>"
        else:
            body += """
            <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
                ⛔ SSRF DIBLOKIR — URL menuju host privat/scheme berbahaya
            </p>
            """
    body += '<form><input name="url" placeholder="http://169.254.169.254/"><button type="submit">Kirim</button></form>'
    body += '<p>Coba: <code>http://127.0.0.1:8000/</code> atau <code>file:///etc/passwd</code></p>'
    return base_page("SSRF Test", body)
