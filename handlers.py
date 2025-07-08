import os
import time
from PIL import Image
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import CHANNEL_ID, GROUP_ID
from database import add_user, get_user, update_collage_ts
from collage import make_collage
from states import CollageStates

IMAGES_DIR = "temp_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

async def check_membership(bot, user_id):
    for chat_id in [CHANNEL_ID, GROUP_ID]:
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

async def handle_start(message: types.Message, bot):
    user_id = message.from_user.id
    if not await check_membership(bot, user_id):
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("Join Channel", url=f"https://t.me/c/{str(CHANNEL_ID)[4:]}"),
            types.InlineKeyboardButton("Join Group", url=f"https://t.me/c/{str(GROUP_ID)[4:]}"),
            types.InlineKeyboardButton("✅ I've Joined", callback_data="joined")
        )
        await message.answer("Please join our channel and group to use the bot.", reply_markup=kb)
        return

    await add_user(user_id)
    await message.answer("👋 Welcome! Send me 4 images to start your collage.")

async def handle_images(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    img_list = data.get("images", [])

    photo = message.photo[-1]
    path = f"{IMAGES_DIR}/{user_id}_{len(img_list)}.jpg"
    await photo.download(destination_file=path)
    img_list.append(path)

    await state.update_data(images=img_list)

    if len(img_list) < 4:
        await message.answer(f"📸 {len(img_list)} image(s) received. Please send {4 - len(img_list)} more.")
    else:
        await state.set_state(CollageStates.waiting_for_grid.state)
        await message.answer(
            "🧩 Choose grid size:",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton("2x2"), KeyboardButton("3x3"), KeyboardButton("4x4")
            )
        )

async def choose_grid(message: types.Message, state: FSMContext):
    if message.text not in ["2x2", "3x3", "4x4"]:
        return await message.answer("Please select a valid grid size.")

    grid = tuple(map(int, message.text.split("x")))
    await state.update_data(grid=grid)

    await state.set_state(CollageStates.waiting_for_background.state)
    await message.answer(
        "🎨 Choose a background color (e.g., white, black, pink, etc.):",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("white", "black", "gray")
    )

async def choose_background(message: types.Message, state: FSMContext):
    bg_color = message.text.lower()
    await state.update_data(background=bg_color)

    await state.set_state(CollageStates.waiting_for_border.state)
    await message.answer(
        "🖌️ Choose a border color (e.g., black, red, blue):",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("black", "red", "blue")
    )

async def choose_border(message: types.Message, state: FSMContext, bot):
    border_color = message.text.lower()
    data = await state.get_data()
    await state.finish()

    grid = data["grid"]
    background = data["background"]
    images_paths = data["images"]

    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        await message.reply("User not found. Use /start first.")
        return

    is_premium, last_ts = user
    now = int(time.time())

    if not is_premium and now - last_ts < 7 * 86400:
        await message.reply("🆓 Free users can create 1 collage per week. Upgrade to Premium for unlimited access.")
        return

    # Load images and create collage
    images = [Image.open(p).resize((300, 300)) for p in images_paths[:grid[0] * grid[1]]]

    collage = make_collage(
        images,
        grid_size=grid,
        border_color=border_color,
        border_width=10,
        bg_color=background
    )

    output_path = f"{IMAGES_DIR}/collage_{user_id}.jpg"
    collage.save(output_path)

    with open(output_path, 'rb') as f:
        await message.answer_photo(f, caption="✨ Here's your collage!")

    await update_collage_ts(user_id, now)

    for p in images_paths:
        os.remove(p)
    os.remove(output_path)