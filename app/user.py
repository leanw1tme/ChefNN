from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.generate_ai import generation_function, format_and_send_recipe
from emoji import emojize

from app.database.requests import set_user
# from middlewares import BaseMiddleware
user = Router()

# user.message.middleware(BaseMiddleware())

class Gen(StatesGroup):
    wait = State()

@user.message(Command("start"))
async def cmd_start(message: Message):
    # kb = [
    #     [
    #         KeyboardButton(text="ingredients_mod"),
    #         KeyboardButton(text="imagination_mod")
    #     ],
    # ]
    # keyboard = ReplyKeyboardMarkup(
    #     keyboard=kb,
    #     resize_keyboard=True,
    #     input_field_placeholder="Commands"
    # )
    await set_user(message.from_user.id)
    await message.answer(emojize(":cook:")+" Hello, "+message.from_user.first_name+"! \n"
                         + "Please enter your ingredients:")
    # await message.answer("Диля лооох " + emojize(":face_savoring_food:"))

# @user.message(F.text.casefold() == "ingredients_mod")
# async def ingredients_mod(message: Message):
#     await message.answer("Enter your ingredients:")

# @user.message(F.text.casefold() == "imagination_mod")
# async def imagination_mod(message: Message):
#     await message.answer("Enter your query:")

@user.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer("Please wait, I am generating a response...")

@user.message()
async def generating(message: Message, state: FSMContext):
    generating_message = await message.answer("Generating recipe... 🍳")
    await state.set_state(Gen.wait)
    ingredients = message.text
    recipes = generation_function([ingredients])
    if recipes:
        for recipe in recipes:
            await format_and_send_recipe(recipe, message)
    else:
        await message.answer("❌ Could not generate a recipe.")

    await generating_message.delete()

    await state.clear()