import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from config import BOT_TOKEN
from handlers import handle_start, handle_images, choose_grid, choose_background, choose_border
from states import CollageStates
from database import init_db, get_user, set_premium

ADMIN_IDS = [7775062794]
ADMIN_USERNAMES = ["lurhe"]

def is_admin(user):
    return user.id in ADMIN_IDS or (user.username and user.username.lower() in ADMIN_USERNAMES)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await handle_start(message, bot)

@dp.message_handler(commands=["collage"])
async def start_collage(message: types.Message, state):
    await message.answer("Send me 4 images to begin.")
    await state.set_state(CollageStates.waiting_for_images.state)

@dp.message_handler(state=CollageStates.waiting_for_images, content_types=ContentType.PHOTO)
async def photo_handler(message: types.Message, state):
    await handle_images(message, state)

@dp.message_handler(state=CollageStates.waiting_for_grid)
async def grid_handler(message: types.Message, state):
    await choose_grid(message, state)

@dp.message_handler(state=CollageStates.waiting_for_background)
async def background_handler(message: types.Message, state):
    await choose_background(message, state)

@dp.message_handler(state=CollageStates.waiting_for_border)
async def border_handler(message: types.Message, state):
    await choose_border(message, state, bot)

@dp.message_handler(commands=["grantpremium"])
async def grant_premium(message: types.Message):
    if not is_admin(message.from_user):
        return await message.reply("❌ You are not authorized to use this command.")
    try:
        user_id = int(message.get_args())
        await set_premium(user_id, 1)
        await message.reply(f"✅ User {user_id} has been granted Premium access.")
    except:
        await message.reply("Usage: /grantpremium <user_id>")

@dp.message_handler(commands=["revokepremium"])
async def revoke_premium(message: types.Message):
    if not is_admin(message.from_user):
        return await message.reply("❌ You are not authorized to use this command.")
    try:
        user_id = int(message.get_args())
        await set_premium(user_id, 0)
        await message.reply(f"🚫 Premium access revoked for user {user_id}.")
    except:
        await message.reply("Usage: /revokepremium <user_id>")

@dp.message_handler(commands=["upgrade"])
async def upgrade_info(message: types.Message):
    await message.answer(
        "💎 *Premium Plan: ₹149/month*\n\n"
        "- Unlimited HD collages\n"
        "- No watermark\n"
        "- Faster delivery\n\n"
        "📤 To upgrade, send payment via UPI to: `Rain@slc`\n"
        "Then send your payment screenshot to @lurhe.\n\n"
        "After verification, you'll be upgraded manually.",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=["me"])
async def check_user(message: types.Message):
    user = await get_user(message.from_user.id)
    if user and user[0]:
        await message.reply("✅ You are a Premium user.")
    else:
        await message.reply("🆓 You are on the Free plan. Use /upgrade to go Premium.")

async def on_startup(_):
    await init_db()
    print("Bot started!")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)