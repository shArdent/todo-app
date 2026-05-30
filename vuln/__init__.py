from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import html

router = APIRouter()

HINT = """
<p style='color:#888;font-size:13px'>
    🙈 Request diterima oleh app. Jika Anda melihat ini, berarti WAF <strong>tidak</strong> memblokir payload Anda.
    App layer sudah meng-escape/mengamankan output — tidak ada eksekusi berbahaya.
</p>
<hr>
"""

STYLE = """
body{font-family:monospace;max-width:700px;margin:auto;padding:20px;background:#111;color:#0f0}
a{color:#0ff} input,textarea,select{width:100%;margin:4px 0;padding:6px;background:#222;color:#0f0;border:1px solid #333}
button{background:#333;color:#0f0;border:1px solid #0f0;padding:6px 14px;cursor:pointer}
.tag{background:#333;color:#fa0;padding:2px 8px;border-radius:4px;font-size:12px}
"""


def base_page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<html><head><title>{html.escape(title)}</title>
<style>{STYLE}</style></head><body>
<h1>{html.escape(title)}</h1>{HINT}{body}
<p><a href='/vuln'>← Back to WAF Lab</a></p></body></html>""")


from vuln.xss import router as xss_router
from vuln.injection import router as injection_router
from vuln.network import router as network_router
from vuln.file_access import router as file_router
from vuln.auth import router as auth_router
from vuln.misc import router as misc_router

router.include_router(xss_router)
router.include_router(injection_router)
router.include_router(network_router)
router.include_router(file_router)
router.include_router(auth_router)
router.include_router(misc_router)


@router.get("/vuln", response_class=HTMLResponse)
async def vuln_dashboard():
    body = """
    <p>Gunakan endpoint di bawah untuk mengirim payload berbahaya. <br>
    <strong>App layer sudah aman</strong> — WAF-lah yang harus mencegat request.</p>

    <h3>Injection</h3>
    <a href="/vuln/sql-injection">SQL Injection <span class="tag">SQLi</span></a>
    <a href="/vuln/ssti">SSTI (Jinja2) <span class="tag">SSTI</span></a>
    <a href="/vuln/command-injection">Command Injection <span class="tag">RCE</span></a>
    <a href="/vuln/ssrf">SSRF <span class="tag">SSRF</span></a>

    <h3>XSS</h3>
    <a href="/vuln/xss/reflected?q=test">Reflected XSS <span class="tag">XSS</span></a>
    <a href="/vuln/xss/stored">Stored XSS <span class="tag">XSS</span></a>

    <h3>Access Control</h3>
    <a href="/vuln/path-traversal">Path Traversal / LFI <span class="tag">LFI</span></a>
    <a href="/vuln/open-redirect?url=https://evil.com">Open Redirect <span class="tag">OpenRedirect</span></a>
    <a href="/vuln/idor/profile?user_id=1">IDOR <span class="tag">IDOR</span></a>
    <a href="/vuln/api/admin">Weak Auth <span class="tag">Auth</span></a>

    <h3>Other</h3>
    <a href="/vuln/upload">File Upload <span class="tag">Upload</span></a>
    <a href="/vuln/api/secret">CORS Misconfig <span class="tag">CORS</span></a>
    <a href="/vuln/crlf?input=test">CRLF / Log Injection <span class="tag">CRLF</span></a>
    <a href="/debug">Debug Info <span class="tag">InfoLeak</span></a>

    <hr>
    <p style="color:#888;font-size:12px">
    🛡️ App layer aman — semua input di-escape, query parameterized, file divalidasi.
    Gunakan WAF untuk mencegat payload berbahaya sebelum mencapai server.
    </p>
    """
    return HTMLResponse(f"""<html><head><title>WAF Test Lab</title>
<style>body{{font-family:monospace;max-width:700px;margin:auto;padding:20px;background:#111;color:#0f0}}
a{{color:#0ff;display:block;margin:8px 0}} h1{{color:#f44;border-bottom:1px solid #333}}
.tag{{background:#333;color:#fa0;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px}}
h3{{color:#0ff;margin-top:24px}}</style></head><body>
<h1>🧪 WAF Test Lab</h1>{body}<p><a href='/'>← Back to Todo</a></p></body></html>""")
