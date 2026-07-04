import aiosqlite

from config import DB_NAME


async def is_premium(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT 1
            FROM premium
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        return await cursor.fetchone() is not None


async def set_premium(telegram_id: int, expire_at: str = None):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO premium (
                telegram_id,
                expire_at
            )
            VALUES (?, ?)
            """,
            (
                telegram_id,
                expire_at,
            ),
        )

        await db.commit()


async def remove_premium(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM premium
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        await db.commit()