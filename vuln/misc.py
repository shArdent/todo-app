from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import html

from vuln import base_page

router = APIRouter()


@router.get("/vuln/crlf", response_class=HTMLResponse)
async def crlf_injection(input: str = ""):
    safe = html.escape(input)
    body = f"""
    <p>CRLF Injection test — input tidak di-log ke file, hanya ditampilkan.</p>
    <p>Input diterima: <code>{safe}</code></p>
    <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
        ⛔ TIDAK ADA LOG INJECTION — stdout hanya menampilkan di console
    </p>
    <form><input name="input" placeholder="test%0d%0aInjected-Header: true"><button type="submit">Kirim</button></form>
    """
    return base_page("CRLF Injection Test", body)


@router.get("/debug")
async def debug_info():
    return JSONResponse({
        "python": "3.13.0",
        "os": "Linux",
        "cwd": "/app",
        "env_vars": {"PATH": "/usr/bin"},
        "note": "Hanya info dummy — tidak ada data sensitif",
    })
