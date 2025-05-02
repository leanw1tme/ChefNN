from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import nest_asyncio
nest_asyncio.apply()


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

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Напиши мне что-нибудь, и я отвечу!")

# Обработка сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    bot_response = generate_response(user_text)
    await update.message.reply_text(bot_response)

# Запуск бота
async def main():
    TOKEN = "7677136072:AAEIg_Tohs-GNCiYWkWVlq_dZsbYxauGzmc"
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")
    await app.run_polling()


import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


