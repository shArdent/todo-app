import aiosqlite

DB_PATH = "todos.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo',
                position INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
            "SELECT * FROM tasks ORDER BY position ASC"
        )
        return [dict(r) for r in rows]

async def create_task(title: str, description: str = "", status: str = "todo"):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM tasks WHERE status = ?",
            (status,)
        )
        row = await cursor.fetchone()
        pos = row[0]
        await db.execute(
            "INSERT INTO tasks (title, description, status, position) VALUES (?, ?, ?, ?)",
            (title, description, status, pos)
        )
        await db.commit()
        return cursor.lastrowid

async def update_task(task_id: int, title: str, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
            (title, description, task_id)
        )
        await db.commit()

async def update_task_status(task_id: int, status: str, position: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status = ?, position = ? WHERE id = ?",
            (status, position, task_id)
        )
        await db.commit()

async def delete_task(task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()
