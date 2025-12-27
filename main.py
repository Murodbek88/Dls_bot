import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = 'SIZNING_BOT_TOKENINGIZ' # BotFather'dan olingan token
CH_ID = '@DLSyuldashev1' # Kanal useri (majburiy obuna uchun)
CH_LINK = 'https://t.me/DLSyuldashev1'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- BAZA BILAN ISHLASH ---
db = sqlite3.connect("bot_bazasi.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, 
    referals INTEGER DEFAULT 0, 
    balance INTEGER DEFAULT 0
)""")
db.commit()

# --- TUGMALAR ---
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("🏆 Referal to'plab akk yutish", "💎 Tanga/Olmos yig'ish")
menu.add("🎁 Tekin akk olish", "🔄 Akk abmen qilish")
menu.add("💰 Akk sotib olish", "🛍️ Akk sotish")

# --- FUNKSIYALAR ---
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CH_ID, user_id=user_id)
        return member.status != 'left'
    except:
        return False

# --- START KOMANDASI ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args() # Referal link orqali kirganini tekshirish

    # Bazaga qo'shish
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        db.commit()
        # Agar kimdir taklif qilgan bo'lsa
        if args and args.isdigit() and int(args) != user_id:
            cursor.execute("UPDATE users SET referals = referals + 1, balance = balance + 10 WHERE user_id = ?", (args,))
            db.commit()

    if await check_sub(user_id):
        await message.answer(
            f"Assalomu alaykum {message.from_user.full_name}!\n"
            f"**dlsyuldashev** botiga xush kelibsiz! ❤️‍🔥",
            reply_markup=menu, parse_mode="Markdown"
        )
    else:
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("Kanalga obuna bo'lish", url=CH_LINK))
        btn.add(InlineKeyboardButton("Tekshirish ✅", callback_data="check"))
        await message.answer(
            "Botdan foydalanish uchun kanalimizga obuna bo'ling! ❤️‍🔥",
            reply_markup=btn
        )

# --- CALLBACK (OBUNANI TEKSHIRISH) ---
@dp.callback_query_handler(text="check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("Rahmat! Botdan foydalanishingiz mumkin.", reply_markup=menu)
    else:
        await call.answer("Siz hali kanalga a'zo emassiz! ⚠️", show_alert=True)

# --- MENYU BO'LIMLARI UCHUN JAVOBLAR ---
@dp.message_handler(content_types=['text'])
async def main_menu(message: types.Message):
    user_id = message.from_user.id
    
    if not await check_sub(user_id):
        await start_cmd(message)
        return

    if message.text == "🏆 Referal to'plab akk yutish":
        cursor.execute("SELECT referals FROM users WHERE user_id = ?", (user_id,))
        ref_count = cursor.fetchone()[0]
        bot_user = (await bot.get_me()).username
        ref_link = f"https://t.me/{bot_user}?start={user_id}"
        await message.answer(f"Sizning referallaringiz: {ref_count} ta\n\nSizning referal silkangiz:\n{ref_link}")

    elif message.text == "💎 Tanga/Olmos yig'ish":
        await message.answer("Tanga va Olmos yig'ish bo'limi yaqin kunlarda ishga tushadi! 🔜")

    elif message.text == "🎁 Tekin akk olish":
        await message.answer("Tekin akkauntlar har yakshanba kanalda e'lon qilinadi!")

    elif message.text == "🔄 Akk abmen qilish":
        await message.answer("Almashish uchun akkauntingiz rasmini va ma'lumotlarini adminga yuboring: @DLSyuldashev_Admin")

    elif message.text == "💰 Akk sotib olish":
        await message.answer("Sotuvdagi akkauntlarni ko'rish uchun kanalimizga o'ting yoki @DLSyuldashev_Admin ga yozing.")

    elif message.text == "🛍️ Akk sotish":
        await message.answer("Akkauntingizni sotmoqchi bo'lsangiz, narxi va rasmlarini @DLSyuldashev_Admin ga yuboring.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
