import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from PIL import Image, ImageDraw, ImageFont

from config import API_TOKEN, holidays, image_configs

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

# BUTTONS
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

for h in holidays.keys():
    keyboard.add(KeyboardButton(h))


# START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Bayramni tanlang:", reply_markup=keyboard)


# HOLIDAY SELECT
@dp.message_handler(lambda message: message.text in holidays)
async def select_holiday(message: types.Message):
    user_data[message.from_user.id] = message.text
    await message.answer("Ism Familiyangizni kiriting:")


# MAIN LOGIC
@dp.message_handler()
async def generate(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_data:
        await message.answer("Avval bayram tanlang")
        return

    folder = holidays[user_data[user_id]]

    if not os.path.exists(folder):
        await message.answer("Texnik ishlar olib borilmoqda. Iltimos, keyinroq urinib ko'ring.")
        return

    images = os.listdir(folder)

    for img_name in images:

        img_path = os.path.join(folder, img_name)

        image = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        config = image_configs.get(img_name)

        # DEFAULT CONFIG
        if not config:
            config = {
                "text": "Hurmat bilan, {name}",
                "color": (47, 82, 178),
                "x": 250,
                "y": 960,
                "size": 35
            }

        font = ImageFont.truetype(
            "fonts/Montserrat-SemiBold.ttf",
            config["size"]
        )

        text = config["text"].format(name=message.text)

        # SHADOW
        draw.text(
            (config["x"] + 2, config["y"] + 2),
            text,
            font=font,
            fill="white"
        )

        # MAIN TEXT
        draw.text(
            (config["x"], config["y"]),
            text,
            font=font,
            fill=config["color"]
        )

        output = f"temp_{img_name}"
        image.save(output)

        with open(output, "rb") as photo:
            await bot.send_photo(message.chat.id, photo)

        os.remove(output)


# RUN
if __name__ == "__main__":
    print("BOT ISHGA TUSHDI")
    executor.start_polling(dp, skip_updates=True)