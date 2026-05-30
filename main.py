from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import jinja2
import os

from database import init_db, get_tasks, create_task, update_task, update_task_status, delete_task
from vuln import router as vuln_router


jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape()
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs("uploads", exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(vuln_router)


def render(template_name: str, **context):
    template = jinja_env.get_template(template_name)
    return HTMLResponse(template.render(**context))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    tasks = await get_tasks()
    columns = {
        "todo": [t for t in tasks if t["status"] == "todo"],
        "in_progress": [t for t in tasks if t["status"] == "in_progress"],
        "done": [t for t in tasks if t["status"] == "done"],
    }
    return render("index.html", request=request, columns=columns)


@app.post("/tasks")
async def add_task(title: str = Form(...), description: str = Form("")):
    await create_task(title, description)
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/edit")
async def edit_task(task_id: int, title: str = Form(...), description: str = Form("")):
    await update_task(task_id, title, description)
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/move")
async def move_task(task_id: int, status: str = Form(...), position: int = Form(0)):
    await update_task_status(task_id, status, position)
    return RedirectResponse(url="/", status_code=303)


@app.post("/tasks/{task_id}/delete")
async def remove_task(task_id: int):
    await delete_task(task_id)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
