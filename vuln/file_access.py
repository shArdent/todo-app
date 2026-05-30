import os
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import HTMLResponse
import html

from vuln import base_page

router = APIRouter()

ALLOWED_DIR = os.path.abspath(".")
ALLOWED_EXTENSIONS = {".txt", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".md"}
MAX_FILE_SIZE = 1024 * 100
UPLOAD_DIR = "uploads"


@router.get("/vuln/path-traversal", response_class=HTMLResponse)
async def path_traversal(file: str = ""):
    safe = html.escape(file)
    body = "<p>Path traversal hanya simulasi — file yang bisa dibaca hanya file di dalam project.</p>"
    if file:
        body += f"""<p>Payload diterima: <code>{safe}</code></p>"""
        full = os.path.normpath(os.path.join(ALLOWED_DIR, file))
        if full.startswith(ALLOWED_DIR):
            try:
                data = open(full).read()
                body += f"<pre>{html.escape(data[:1000])}</pre>"
            except Exception:
                body += "<p>File tidak ditemukan (aman).</p>"
        else:
            body += f"""
            <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
                ⛔ PATH TRAVERSAL DIBLOKIR — hanya bisa akses dalam project
            </p>
            <p>Path yang dinormalisasi: <code>{html.escape(full)}</code> (di luar direktori)</p>
            """
    body += '<form><input name="file" placeholder="../../../etc/passwd"><button type="submit">Kirim</button></form>'
    body += '<p>Coba: <code>../../../etc/passwd</code> — WAF harus blokir.</p>'
    return base_page("Path Traversal Test", body)


@router.get("/vuln/upload", response_class=HTMLResponse)
async def upload_form():
    body = f"""
    <p>Upload file — hanya ekstensi gambar/teks yang diizinkan (max 100KB).</p>
    <p>Ekstensi diizinkan: {', '.join(ALLOWED_EXTENSIONS)}</p>
    <form action="/vuln/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file"><button type="submit">Upload</button>
    </form>
    <p>Coba upload: <code>.php</code>, <code>.asp</code>, <code>.jsp</code>, <code>.exe</code> — WAF harus blokir.</p>
    """
    return base_page("File Upload Test", body)


@router.post("/vuln/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return base_page("Upload Ditolak", f"""
        <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
            ⛔ FILE DITOLAK — ekstensi <code>{html.escape(ext)}</code> tidak diizinkan
        </p>
        <p>Ekstensi yang diizinkan: {', '.join(ALLOWED_EXTENSIONS)}</p>
        """)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return base_page("Upload Ditolak", """
        <p class="tag" style="background:#f44;color:#fff;padding:4px 8px">
            ⛔ FILE DITOLAK — melebihi 100KB
        </p>
        """)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
    with open(path, "wb") as f:
        f.write(content)

    return base_page("Upload Berhasil", f"""
    <p>File <code>{html.escape(file.filename)}</code> terupload!</p>
    <p><a href="/uploads/{html.escape(file.filename)}">Lihat file</a></p>
    """)
