from datetime import datetime
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app import keyboards as kb
from app.database.requests import stock
from app.message_storage import remove_all_messages, add_messages

router = Router()

def get_greeting() -> str:
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        return 'Доброе утро'
    elif 12 <= current_hour < 18:
        return 'Добрый день'
    elif 18 <= current_hour < 22:
        return 'Добрый вечер'
    else:
        return 'Доброй ночи'


@router.message(CommandStart())
async def start(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)

    greeting = get_greeting()
    await message.answer(f'{greeting}, {message.from_user.first_name}', reply_markup=kb.main)

@router.message(F.text == 'Отмена')
async def cancel(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    greeting = get_greeting()
    await state.clear()
    await message.answer(f'И снова {greeting}', reply_markup=kb.main)


@router.message(F.text == 'Остаток')
async def product_stock_balance(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)

    message_ids = []
    products = await stock()
    
    if not products:
        await message.answer("Нет данных о продуктах.")
        return

    for product_id, product_name, balance in products:
        text = f"Продукт: {product_name}\n" \
                f"Остаток: {balance}"
        sent_message = await message.answer(text)
        message_ids.append(sent_message.message_id)

    await add_messages(message.from_user.id, message_ids)