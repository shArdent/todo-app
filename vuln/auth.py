from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import html

from vuln import base_page

router = APIRouter()


@router.get("/vuln/idor/profile", response_class=HTMLResponse)
async def idor_profile(user_id: int = 1):
    safe_id = html.escape(str(user_id))
    body = f"""
    <p>Profile user — tidak ada data sensitif yang bocor.</p>
    <p>User ID: {safe_id}</p>
    <p>Username: user_{safe_id}</p>
    <p>Email: user_{safe_id}@todo.test</p>
    <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
        ⛔ TIDAK ADA DATA SENSITIF — hanya placeholder
    </p>
    <p>Coba akses: <a href="?user_id=1">user 1</a> <a href="?user_id=2">user 2</a> <a href="?user_id=3">user 3</a></p>
    """
    return base_page("IDOR Test", body)


@router.get("/vuln/api/secret")
async def cors_secret():
    return JSONResponse(
        content={"api_key": "TEST_KEY_DEADBEEF", "secret": "TEST_FLAG_WAF_BYPASS"},
        headers={"Access-Control-Allow-Origin": "*"},
    )


@router.get("/vuln/api/admin", response_class=HTMLResponse)
async def admin_api(token: str = ""):
    body = f"<p>Token diterima: <code>{html.escape(token)}</code></p>"
    body += '<form><input name="token" placeholder="admin123"><button type="submit">Kirim</button></form>'
    return base_page("Weak Auth Test", body)
