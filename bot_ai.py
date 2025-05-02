import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F, Router
from transformers import AutoModelForCausalLM, AutoTokenizer

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7981798598:AAEYrCHuwCOUDGTlfc2Y5c-G27vOpwKo5WE")
# Диспетчер
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="ingredients_mod"),
            types.KeyboardButton(text="imagination_mod")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Commands"
    )
    await message.answer("Hello!", reply_markup=keyboard)
    

@router.message(F.text.casefold() == "ingredients_mod")
async def ingredients_mod(message: types.Message):
    await message.answer("Enter your ingredients:")

@router.message(F.text.casefold() == "imagination_mod")
async def imagination_mod(message: types.Message):
    await message.answer("Enter your query:")
    
# Загрузка модели
# model_path = "./model"
model_name = 'pratultandon/recipe-nlg-gpt2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

# Функция генерации текста
def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_length=100, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Обработка сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    bot_response = generate_response(user_text)
    await update.message.reply_text(bot_response)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())