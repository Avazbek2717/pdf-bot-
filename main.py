from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.types.message import ContentType
from PIL import Image
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')


bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


user_images = {}
user_pdf_names = {}

@router.message(Command("start"))
async def start_command_handler(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Rasmlarni PDF fayliga aylantiruvchi botga xush kelibsiz.\n"
        "Rasmlarni yuboring va oxirida /done buyrug'ini bosing. PDF nomini kiritish uchun ham tayyor bo'ling."
    )

@router.message(lambda message: message.content_type == ContentType.PHOTO)
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id


    file = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file.file_path)

    
    user_dir = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    image_path = os.path.join(user_dir, f"{len(os.listdir(user_dir)) + 1}.jpg")

    with open(image_path, "wb") as img_file:
        img_file.write(downloaded_file.getvalue())


    if user_id not in user_images:
        user_images[user_id] = []
    user_images[user_id].append(image_path)

    await message.reply("Rasm qabul qilindi. Yana yuboring yoki /done buyrug'ini yuboring.")

@router.message(Command("done"))
async def ask_pdf_name_handler(message: types.Message):
    user_id = message.from_user.id

    
    if user_id not in user_images or not user_images[user_id]:
        await message.reply("Avval rasm yuboring!")
        return

    await message.reply("PDF fayl uchun nom kiriting:")

    user_pdf_names[user_id] = None

@router.message(lambda message: message.from_user.id in user_pdf_names and user_pdf_names[message.from_user.id] is None)
async def save_pdf_name_handler(message: types.Message):
    user_id = message.from_user.id
    pdf_name = message.text.strip()

    if not pdf_name.endswith(".pdf"):
        pdf_name += ".pdf"

    user_pdf_names[user_id] = pdf_name

    image_paths = user_images[user_id]
    images = [Image.open(img).convert("RGB") for img in image_paths]
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    await message.reply_document(FSInputFile(pdf_path))


    for img_path in image_paths:
        os.remove(img_path)
    os.remove(pdf_path)
    del user_images[user_id]
    del user_pdf_names[user_id]

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

