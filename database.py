import aiosqlite

async def init_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                is_premium INTEGER DEFAULT 0,
                last_collage_ts INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def add_user(user_id: int):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT is_premium, last_collage_ts FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_collage_ts(user_id: int, timestamp: int):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("UPDATE users SET last_collage_ts = ? WHERE user_id = ?", (timestamp, user_id))
        await db.commit()

async def set_premium(user_id: int, status: int):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("UPDATE users SET is_premium = ? WHERE user_id = ?", (status, user_id))
        await db.commit()