from telethon import TelegramClient, functions
from telethon.tl.types import User
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError
from pathlib import Path
from config import API_ID, API_HASH

client = TelegramClient(
    "sessions/osint",
    API_ID,
    API_HASH
)

async def connect():
    if not client.is_connected():
        await client.start()

async def disconnect():
    if client.is_connected():
        await client.disconnect()

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def download_profile_photo(entity):
    await connect()
    path = await client.download_profile_photo(
        entity,
        file=DOWNLOAD_DIR
    )
    return path


async def search_by_id(user_id: int):
    """ID bo'yicha qidiruv — kesh, keyin guruhlar orqali"""
    
    # 1. Avval keshdan
    try:
        user = await client.get_entity(user_id)
        if isinstance(user, User):
            return user
    except Exception:
        pass

    # 2. Keshda yo'q bo'lsa — guruhlarda qidiramiz
    try:
        async for dialog in client.iter_dialogs():
            if not (dialog.is_group or dialog.is_channel):
                continue
            try:
                async for member in client.iter_participants(dialog):
                    if member.id == user_id:
                        return member
            except Exception:
                continue
    except Exception:
        pass

    return None


async def search_entity(query: str):
    await connect()
    
    print(f"Query: {query}")
    
    try:
        # --- USERNAME bo'yicha ---
        if query.startswith("@"):
            username = query[1:]
            print(f"Username: {username}")
            
            result = await client(
                functions.contacts.ResolveUsernameRequest(username)
            )
            
            if not result.users:
                print("Username topilmadi")
                return None
            
            user = result.users[0]

        # --- ID bo'yicha ---
        else:
            try:
                user_id = int(query)
            except ValueError:
                print("Noto'g'ri format — @ yoki raqam kiriting")
                return None
            
            print(f"ID bo'yicha qidirilmoqda: {user_id}")
            user = await search_by_id(user_id)
            
            if user is None:
                print("ID bo'yicha topilmadi")
                return None

        # --- Natija ---
        if not isinstance(user, User):
            print("Bu foydalanuvchi emas (bot yoki kanal bo'lishi mumkin)")
            return None

        return {
            "entity": user,
            "type": "user",
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username,
            "bot": user.bot,
            "verified": user.verified,
            "premium": getattr(user, "premium", False),
            "scam": user.scam,
            "fake": user.fake,
            "photo": user.photo is not None,
            "lang_code": getattr(user, "lang_code", None),
        }

    except UsernameInvalidError:
        print("Username noto'g'ri")
        return None
    except UsernameNotOccupiedError:
        print("Username mavjud emas")
        return None
    except Exception:
        import traceback
        traceback.print_exc()
        return None