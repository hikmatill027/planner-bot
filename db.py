import aiosqlite
from datetime import date

DB_PATH = "planner.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                date TEXT PRIMARY KEY,
                raw_text TEXT,
                formatted_text TEXT,
                created_at TEXT
            )
        """)
        await db.commit()

async def save_plan(raw_text: str, formatted_text: str):
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO plans (date, raw_text, formatted_text, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (today, raw_text, formatted_text))
        await db.commit()

async def get_plan_for_date(target_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT formatted_text FROM plans WHERE date = ?", (target_date,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
        
async def get_raw_plan_for_date(target_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT raw_text FROM plans WHERE date = ?", (target_date,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None