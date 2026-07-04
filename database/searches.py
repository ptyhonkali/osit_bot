import aiosqlite

from config import DB_NAME


async def add_search(user_id: int, query: str, module: str, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO searches (
                telegram_id,
                query,
                module,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                query,
                module,
                status,
            ),
        )

        await db.commit()


async def get_today_search_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM searches
            WHERE user_id = ?
            AND DATE(created_at) = DATE('now','localtime')
            """,
            (user_id,),
        )

        result = await cursor.fetchone()

        return result[0]


async def get_search_history(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                query,
                module,
                status,
                created_at
            FROM searches
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        return await cursor.fetchall()