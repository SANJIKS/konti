from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.message_storage import add_messages, remove_all_messages
from app.states import StockInCreateForm, StockOutCreateForm
from app import keyboards as kb
from app.database.requests import delete_stock_in, delete_stock_out, stock_in_detail_request, stock_in_request, create_stock_in, create_stock_out, stock_out_detail_request, get_product_balance

router = Router()

@router.message(F.text == 'Приход')
async def stock_in_list(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message_1 = await message.answer('Список всех Приходов:', reply_markup=await kb.stock_ins())
    sent_message_2 = await message.answer('Для добавления Прихода нажмите "Добавить приход"', reply_markup=kb.add_stock_in)
    await add_messages(message.from_user.id, [sent_message_1.message_id, sent_message_2.message_id])

@router.message(F.text == 'Уход')
async def stock_out_list(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message_1 = await message.answer('Список всех Уходов:', reply_markup=await kb.stock_out())
    sent_message_2 = await message.answer('Для добавления Ухода нажмите "Добавить уход"', reply_markup=kb.add_stock_out)
    await add_messages(message.from_user.id, [sent_message_1.message_id, sent_message_2.message_id])


@router.message(F.text == 'Добавить приход')
async def add_stock_in(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Выберите товар прихода: ', reply_markup=await kb.products_for_stock())
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.set_state(StockInCreateForm.product)

@router.callback_query(StockInCreateForm.product)
async def product_add_stock_in(callback: Message, state: FSMContext):
    await remove_all_messages(callback.from_user.id, callback.bot)
    sent_message = await callback.message.answer('Введите количество')
    product_id = callback.data.split('_')[3]
    await state.update_data(product_id=product_id)
    await state.set_state(StockInCreateForm.quantity)
    await add_messages(callback.from_user.id, [sent_message.message_id])

@router.message(StockInCreateForm.quantity)
async def final_add_stock_in(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    try:
        data = await state.get_data()
        quantity = int(message.text)
        product_id = data.get('product_id')

        await create_stock_in(product_id=product_id, quantity=quantity)

        stock_balance = await get_product_balance(product_id)

        sent_message = await message.answer(
            f"Приход успешно добавлен!\nОстаток товара: {stock_balance}\n", 
            reply_markup=kb.main
        )
        await state.clear()
        await add_messages(message.from_user.id, sent_message.message_id)

    except ValueError:
        await message.answer('Для количества нужно писать цифры!')


@router.message(F.text == 'Добавить уход')
async def add_stock_out(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Выберите товар уход: ', reply_markup=await kb.products_for_stock())
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.set_state(StockOutCreateForm.product)

@router.callback_query(StockOutCreateForm.product)
async def product_add_stock_out(callback: Message, state: FSMContext):
    await remove_all_messages(callback.from_user.id, callback.bot)
    sent_message = await callback.message.answer('Введите количество')
    product_id = callback.data.split('_')[3]
    await state.update_data(product_id=product_id)
    await state.set_state(StockOutCreateForm.quantity)
    await add_messages(callback.from_user.id, [sent_message.message_id])

@router.message(StockOutCreateForm.quantity)
async def final_add_stock_out(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    try:
        data = await state.get_data()
        quantity = int(message.text)
        product_id = data.get('product_id')

        await create_stock_out(product_id=product_id, quantity=quantity)
        stock_balance = await get_product_balance(product_id)
        sent_message = await message.answer(
            f"Уход успешно добавлен!\nОстаток товара: {stock_balance}\n", 
            reply_markup=kb.main
        )
        await state.clear()
        await add_messages(message.from_user.id, sent_message.message_id)

    except ValueError:
        await message.answer('Для количества нужно писать цифры!')


@router.callback_query(F.data.startswith('stock_in_rm_'))
async def remove_stock_in(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    stock_in_id = callback.data.split('_')[3]
    await delete_stock_in(stock_in_id)
    sent_message = await callback.message.answer('Приход успешно удалён!')
    await add_messages(callback.from_user.id, [sent_message.message_id])
    await stock_in_list(callback.message)

@router.callback_query(F.data.startswith('stock_out_rm_'))
async def remove_stock_out(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    stock_out_id = callback.data.split('_')[3]
    await delete_stock_out(stock_out_id)
    sent_message = await callback.message.answer('Уход успешно удалён!')
    await add_messages(callback.from_user.id, [sent_message.message_id])
    await stock_out_list(callback.message)


@router.callback_query(F.data.startswith('stock_in_'))
async def stock_in_detail(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    stock_in_id = callback.data.split('_')[2]
    stock_in = await stock_in_detail_request(stock_in_id)
    product_name = stock_in.product.name
    product_price = stock_in.product.price
    total_sum = stock_in.quantity * product_price
    formatted_date = stock_in.timestamp.strftime("%d-%m-%Y %H:%M:%S")

    text = f"Номер прихода: {stock_in.id}\n" \
           f"Продукт: {product_name}\n" \
           f"Количество: {stock_in.quantity}\n" \
           f"Сумма: {total_sum:.2f}\n" \
           f"Дата: {formatted_date}\n"

    sent_message = await callback.message.answer(text, reply_markup=await kb.delete_update_stock_in(stock_in_id))
    sent_message_2 = await callback.message.answer('Для добавления прихода нажмите "Добавить приход"', reply_markup=kb.add_stock_in_detail)
    await add_messages(callback.from_user.id, [sent_message.message_id, sent_message_2.message_id])


@router.callback_query(F.data.startswith('stock_out_'))
async def stock_out_detail(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    stock_out_id = callback.data.split('_')[2]
    stock_out = await stock_out_detail_request(stock_out_id)
    product_name = stock_out.product.name
    product_price = stock_out.product.price
    total_sum = stock_out.quantity * product_price
    formatted_date = stock_out.timestamp.strftime("%d-%m-%Y %H:%M:%S")

    text = f"Номер ухода: {stock_out.id}\n" \
           f"Продукт: {product_name}\n" \
           f"Количество: {stock_out.quantity}\n" \
           f"Сумма: {total_sum:.2f}\n" \
           f"Дата: {formatted_date}\n"

    sent_message = await callback.message.answer(text, reply_markup=await kb.delete_update_stock_out(stock_out_id))
    sent_message_2 = await callback.message.answer('Для добавления ухода нажмите "Добавить приход"', reply_markup=kb.add_stock_out_detail)
    await add_messages(callback.from_user.id, [sent_message.message_id, sent_message_2.message_id])