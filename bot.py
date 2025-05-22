import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import logging

# .env fayldan tokenni o'qish
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # <--- TO‘G‘RI USUL

ADMIN_IDS = [7105959922, 1234567890]  # <-- O'z admin ID'ingizni kiriting

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)  # <--- TO‘G‘RI NOM
dp = Dispatcher()

# Foydalanuvchi tillarini saqlash uchun dictionary
user_language = {}

# Til tanlash tugmalari
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

# /start komandasi
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=language_keyboard())

# Til tanlanganda
@dp.callback_query(F.data.startswith("lang_"))
async def language_chosen(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_language[user_id] = lang

    if lang == "uz":
        text = (
            "Assalomu alaykum, bu ePochta portalining murojaat boti.\n\n"
            "Ariza va shikoyatingiz yoki fosh etuvchi ma’lumotingiz bo‘lsa, "
            "mazmunini qisqacha tushuntirib yozing. Hujjatlar, foto, audio va "
            "videolar bo‘lsa ilova qilib yo‘llang. Aloqa uchun telegram manzilingizni yozib yuboring."
        )
    else:
        text = (
            "Здравствуйте. Это бот для обращений портала ePochta.\n\n"
            "Если у вас есть жалоба или разоблачающая информация, кратко опишите суть. "
            "Прикрепите документы, фото, аудио или видео, если имеются. "
            "Укажите ваш Telegram для связи."
        )

    await callback.message.answer(text)
    await callback.answer()

# Xabarlar uchun handler
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, "uz")

    if lang == "uz":
        response_text = "✅ Murojaatingiz qabul qilindi. Adminlar ko‘rib chiqadi."
    else:
        response_text = "✅ Ваше обращение принято. Администраторы рассмотрят его."

    await message.answer(response_text)

    for admin_id in ADMIN_IDS:
        try:
            await bot.forward_message(chat_id=admin_id, from_chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logging.error(f"Xabarni admin {admin_id} ga yuborishda xato: {e}")

# Asosiy loop
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
