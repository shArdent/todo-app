from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import html

from database import get_tasks
from vuln import base_page

router = APIRouter()


@router.get("/vuln/xss/reflected", response_class=HTMLResponse)
async def xss_reflected(q: str = ""):
    safe = html.escape(q)
    body = f"""
    <p>Query Anda: <strong>{safe}</strong></p>
    <p>Payload mentah yang diterima: <code>{safe}</code></p>
    <form><input name="q" placeholder="&lt;script&gt;alert(1)&lt;/script&gt;"><button type="submit">Kirim</button></form>
    <p>Coba: <code>&lt;script&gt;alert(1)&lt;/script&gt;</code></p>
    """
    return base_page("Reflected XSS Test", body)


@router.get("/vuln/xss/stored", response_class=HTMLResponse)
async def xss_stored():
    tasks = await get_tasks()
    rows = ""
    for t in tasks:
        rows += (
            f"<tr><td>{html.escape(str(t['id']))}</td>"
            f"<td>{html.escape(t['title'])}</td>"
            f"<td>{html.escape(t['description'])}</td></tr>"
        )
    body = f"""
    <p>Data task ditampilkan dengan <code>html.escape()</code> — XSS tidak akan jalan.</p>
    <table border=1 style='border-collapse:collapse;width:100%'>
    <tr><th>ID</th><th>Title</th><th>Description</th></tr>{rows}</table>
    """
    return base_page("Stored XSS Test", body)
