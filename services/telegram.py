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
        await client.start()   # connect() emas, start()


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

async def search_user(query: str):
    await connect()

    print(f"Query: {query}")
    print(type(query), query)
    try:
        if query.startswith("@"):
            username = query[1:]
            print(f"Username: {username}")

            result = await client(
                functions.contacts.ResolveUsernameRequest(username)
            )

            print(result)

            if not result.users:
                return None

            user = result.users[0]

        else:
            user = await client.get_entity(int(query))

        print(user)

        return {
            "entity": user,
            "type": "user",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "bot": user.bot,
            "verified": user.verified,
            "premium": getattr(user, "premium", False),
            "scam": user.scam,
            "fake": user.fake,
            "photo": user.photo is not None,
            "lang_code": getattr(user, "lang_code", None),
        }


    except (UsernameInvalidError, UsernameNotOccupiedError):
        print("Username topilmadi")
        return None

    except ValueError:
        print("ID noto'g'ri")
        return None

    except Exception:
        import traceback
        traceback.print_exc()
        return None