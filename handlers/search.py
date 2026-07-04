from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from states.search import SearchState
from services.telegram import search_entity, download_profile_photo

# === Yangi importlar ===
from database.premium import is_premium
from config import FREE_SEARCH_LIMIT
from database.searches import (
    add_search,
    get_today_search_count,
)
from database.premium import is_premium

router = Router()


@router.message(F.text == "🔍 Qidiruv")
async def search_start(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await message.answer(
        "🔎 Username yoki Telegram ID yuboring.\n\n"
        "Misol:\n"
        "@username\n"
        "yoki\n"
        "123456789\n"
        "id bo'yicha qidiruv uzoqroq vaqt olishi mumkin."
    )


@router.message(SearchState.waiting_query)
async def process_query(message: Message, state: FSMContext):
    query = message.text.strip()
    user_id = message.from_user.id

    # === Bepul limit tekshiruvi ===
    if not await is_premium(user_id):
        count = await get_today_search_count(user_id)
        if count >= FREE_SEARCH_LIMIT:
            await message.answer(
                "👑 Bugungi bepul limit tugadi.\n\n"
                "Premium sotib olib cheksiz qidiruvdan foydalanishingiz mumkin."
            )
            await state.clear()
            return

    waiting = await message.answer("⏳ Qidiruv amalga oshirilmoqda...")

    result = await search_entity(query)

    if not result:
        await waiting.edit_text("❌ Foydalanuvchi topilmadi.")
        await state.clear()
        
        # === Muvaffaqiyatsiz qidiruvni bazaga yozish ===
        await add_search(
            user_id=user_id,
            query=query,
            module="telegram",
            status="failed",
        )
        return

    # Muvaffaqiyatli natija
    first_name = result.get("first_name") or "-"
    last_name = result.get("last_name") or "-"
    username = (
        f"@{result['username']}"
        if result.get("username")
        else "Mavjud emas"
    )
    profile_link = (
        f"https://t.me/{result['username']}"
        if result.get("username")
        else "Mavjud emas"
    )

    text = (
        "🕵️ <b>Telegram OSINT</b>\n\n"
        f"👤 <b>Ism:</b> {first_name}\n"
        f"👥 <b>Familiya:</b> {last_name}\n"
        f"🆔 <b>ID:</b> <code>{result['id']}</code>\n"
        f"📛 <b>Username:</b> {username}\n"
        f"🔗 <b>Profil:</b> {profile_link}\n\n"
        f"🤖 <b>Bot:</b> {'✅' if result['bot'] else '❌'}\n"
        f"⭐ <b>Premium:</b> {'✅' if result['premium'] else '❌'}\n"
        f"✔️ <b>Verified:</b> {'✅' if result['verified'] else '❌'}\n"
        f"🚫 <b>Scam:</b> {'✅' if result['scam'] else '❌'}\n"
        f"🎭 <b>Fake:</b> {'✅' if result['fake'] else '❌'}"
    )

    try:
        photo_path = await download_profile_photo(result["entity"])
        if photo_path:
            photo = FSInputFile(photo_path)
            await waiting.delete()
            await message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode="HTML"
            )
        else:
            await waiting.edit_text(text, parse_mode="HTML")
    except Exception as e:
        print(e)
        await waiting.edit_text(text, parse_mode="HTML")

    # === Muvaffaqiyatli qidiruvni bazaga yozish ===
    await add_search(
        user_id=user_id,
        query=query,
        module="telegram",
        status="success",
    )

    await state.clear()