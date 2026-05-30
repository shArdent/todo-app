# 📋 Kanban Todo + 🧪 WAF Test Lab

Proyek ini terdiri dari dua bagian:

1. **Kanban Todo App** — Aplikasi manajemen task sederhana dengan drag-and-drop
2. **WAF Test Lab** — Sarana pengujian WAF (Web Application Firewall) dengan endpoint yang **tampak** rentan tetapi **aman** di application layer

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Web Framework | FastAPI (Python) |
| Database | SQLite via aiosqlite (async) |
| Template | Jinja2 (autoescape ON) |
| Server | Uvicorn |
| Frontend | Vanilla JS, CSS |

---

## Struktur Proyek

```
todo-app/
├── main.py                      # Entry point — Kanban Todo App
├── database.py                  # Operasi database (parameterized query)
├── requirements.txt             # Dependencies
├── .gitignore
├── templates/
│   └── index.html               # Halaman utama todo
├── static/
│   ├── app.js                   # Drag-and-drop logic
│   └── style.css                # Styling
├── vuln/                        # 🔴 WAF Test Lab Package
│   ├── __init__.py              # Router utama, base_page, dashboard /vuln
│   ├── xss.py                   # Reflected & Stored XSS test
│   ├── injection.py             # SQLi, Command Injection, SSTI test
│   ├── network.py               # SSRF, Open Redirect test
│   ├── file_access.py           # Path Traversal, File Upload test
│   ├── auth.py                  # IDOR, CORS, Weak Auth test
│   └── misc.py                  # CRLF, Debug info leak test
└── uploads/                     # Upload directory (di-gitignore)
```

---

## Cara Menjalankan

```bash
pip install -r requirements.txt
python main.py
# atau
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Akses di **http://localhost:8000**

---

## 📋 Kanban Todo App

### Endpoints

| Method | Path | Deskripsi |
|---|---|---|
| GET | `/` | Halaman utama — board Kanban |
| POST | `/tasks` | Buat task baru |
| POST | `/tasks/{id}/edit` | Edit task |
| POST | `/tasks/{id}/move` | Pindah status/posisi task |
| POST | `/tasks/{id}/delete` | Hapus task |

### Fitur
- Drag-and-drop antar kolom (To Do → In Progress → Done)
- Add task via modal
- Edit task via modal inline
- Delete task

---

## 🧪 WAF Test Lab

Dashboard: **`/vuln`**

Semua endpoint WAF Test Lab **sudah aman di application layer**:

- Input user di-escape dengan `html.escape()`
- Query database menggunakan **parameterized query**
- Tidak ada eksekusi shell/command
- File upload divalidasi ekstensi & ukuran
- Redirect hanya ke whitelist path internal
- SSRF hanya mengizinkan host publik
- Data yang ditampilkan adalah dummy — tidak ada rahasia

Tujuan endpoint ini adalah **mengirim request berbahaya** dan memverifikasi apakah WAF berhasil mencegatnya sebelum mencapai server.

### Endpoint Pengujian

#### Injection

| Endpoint | Parameter | Metode Serangan | Contoh Payload |
|---|---|---|---|
| `GET /vuln/sql-injection` | `?id=` | SQL Injection | `1 UNION SELECT 1,2,3,4,5,6` |
| `GET /vuln/command-injection` | `?host=` | Command Injection / RCE | `127.0.0.1; cat /etc/passwd` |
| `GET /vuln/ssti` | `?name=` | SSTI (Server-Side Template Injection) | `{{config}}` atau `{{7*7}}` |

#### XSS

| Endpoint | Parameter | Metode Serangan | Contoh Payload |
|---|---|---|---|
| `GET /vuln/xss/reflected` | `?q=` | Reflected XSS | `<script>alert(1)</script>` |
| `GET /vuln/xss/stored` | — | Stored XSS | Buat task dengan `<script>` di judul/deskripsi |

#### Access Control

| Endpoint | Parameter | Metode Serangan | Contoh Payload |
|---|---|---|---|
| `GET /vuln/path-traversal` | `?file=` | LFI / Path Traversal | `../../../etc/passwd` |
| `GET /vuln/open-redirect` | `?url=` | Open Redirect | `https://evil.com` |
| `GET /vuln/idor/profile` | `?user_id=` | IDOR | `?user_id=2` (akses user lain) |
| `GET /vuln/api/admin` | `?token=` | Weak Auth / Token in URL | `admin123` |

#### Network

| Endpoint | Parameter | Metode Serangan | Contoh Payload |
|---|---|---|---|
| `GET /vuln/ssrf` | `?url=` | SSRF | `http://169.254.169.254/`, `file:///etc/passwd` |

#### File Upload

| Endpoint | Metode Serangan | Contoh Payload |
|---|---|---|
| `GET /vuln/upload` | Unrestricted File Upload | Upload `.php`, `.asp`, `.exe` |
| `POST /vuln/upload` | Upload file dengan ekstensi terlarang | |

#### Other

| Endpoint | Parameter | Metode Serangan | Contoh Payload |
|---|---|---|---|
| `GET /vuln/api/secret` | — | CORS Misconfig | Akses dari origin lain |
| `GET /vuln/crlf` | `?input=` | CRLF / Log Injection | `test%0d%0aInjected-Header: true` |
| `GET /debug` | — | Information Leak / Debug endpoint | |

### Keamanan Application Layer

Setiap endpoint telah diamankan dengan mekanisme berikut:

| Celah | Mekanisme Keamanan |
|---|---|
| SQL Injection | Parameterized query (`WHERE id = ?`) |
| XSS | `html.escape()` pada semua output |
| Command Injection | Tidak ada eksekusi shell — hanya simulasi |
| SSTI | Jinja2 autoescape ON |
| Path Traversal | Path dinormalisasi & dibatasi dalam project root |
| Open Redirect | Whitelist path internal |
| SSRF | Blokir IP privat (`127.0.0.1`, `169.254.169.254`, dll) & skema berbahaya (`file://`) |
| File Upload | Filter ekstensi (`.txt`, `.jpg`, `.png`, dll) + max 100KB |
| IDOR | Data dummy — tidak ada informasi sensitif |
| CORS | Mengembalikan data dummy |
| Debug | Informasi server palsu |

---

## Keamanan Deployment

⚠️ **Peringatan:** Meskipun application layer sudah aman, endpoint WAF Test Lab tetap **tidak boleh diakses publik tanpa WAF**. Gunakan untuk:

- Pengujian WAF (ModSecurity, Cloudflare WAF, AWS WAF, dll)
- Training dan simulasi serangan
- Validasi rule WAF
- Penetration testing internal

### Rekomendasi Deployment

```bash
# Hanya untuk akses lokal (tanpa WAF)
python main.py

# Untuk pengujian dengan WAF, deploy di belakang reverse proxy
# (nginx + ModSecurity, Cloudflare, AWS WAF, dll)
```
