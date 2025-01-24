from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.message_storage import remove_all_messages, add_messages
from app.states import ProductCreateForm, ProductUpdateForm, CategoryCreateForm
from app import keyboards as kb
from app.database.requests import create_product, delete_product, request_product, update_product_field, create_category, delete_category

router = Router()

@router.message(F.text == 'Товары')
async def categories(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Категория товаров?', reply_markup=await kb.categories())
    second_sent_message = await message.answer('Можете добавить категорию, для этого нажмите "Добавить категорию"', reply_markup=kb.add_category)
    await add_messages(message.from_user.id, [sent_message.message_id, second_sent_message.message_id])


@router.callback_query(F.data.startswith('products_cg_'))
async def products(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    category_id = callback.data.split('_')[2]
    await callback.message.answer('Товары:', reply_markup=await kb.products(category_id))
    sent_message = await callback.message.answer('Для добавления нового товара нажмите "Добавить товар"', reply_markup=kb.add_product_detail)
    await add_messages(callback.from_user.id, sent_message.message_id)

@router.message(F.text == 'Добавить категорию')
async def add_category(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Введите название категории')
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.set_state(CategoryCreateForm.name)

@router.message(CategoryCreateForm.name)
async def name_add_category(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    await create_category(message.text)
    sent_message = await message.answer('Категория успешно создана!', reply_markup=await kb.categories())
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.clear()


@router.message(F.text == 'Добавить товар')
async def add_product(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Выберите категорию продукта: ', reply_markup=await kb.categories_list())
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.set_state(ProductCreateForm.category)

@router.callback_query(ProductCreateForm.category)
async def name_add_product(callback: CallbackQuery, state: FSMContext):
    await remove_all_messages(callback.from_user.id, callback.bot)
    await state.update_data(category_id=callback.data.split('_')[1])
    sent_message = await callback.message.answer('Введите название товара')
    await add_messages(callback.from_user.id, [sent_message.message_id])
    await state.set_state(ProductCreateForm.name)

@router.message(ProductCreateForm.name)
async def price_add_product(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    await state.update_data(name=message.text)
    sent_message = await message.answer('Укажите цену')
    await add_messages(message.from_user.id, [sent_message.message_id])
    await state.set_state(ProductCreateForm.price)

@router.message(ProductCreateForm.price)
async def final_add_product(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    try:
        data = await state.get_data()
        price = float(message.text)
        name = data.get('name')
        category_id = data.get('category_id')

        await create_product(category_id=category_id, name=name, price=price)
        sent_message = await message.answer('Товар успешно создан!', reply_markup=await kb.products(category_id))
        await add_messages(message.from_user.id, [sent_message.message_id])
        await state.clear()

    except ValueError:
        await message.answer('Для числа нужны только цифры! Например 100 или 100.00')


@router.callback_query(F.data.startswith('product_rm_'))
async def remove_product(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    product_id = callback.data.split('_')[2]
    sent_message = await callback.message.answer('Товар успешно удалён!')
    await add_messages(callback.from_user.id, [sent_message.message_id])
    await delete_product(product_id)


@router.message(F.text == 'Удалить категорию')
async def remove_category(message: Message):
    await remove_all_messages(message.from_user.id, message.bot)
    sent_message = await message.answer('Выберите категорию для удаления: ', reply_markup=await kb.categories_for_del())
    await add_messages(message.from_user.id, [sent_message.message_id])

@router.callback_query(F.data.startswith('category_rm_'))
async def final_remove_category(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    category_id = callback.data.split('_')[2]
    sent_message = await callback.message.answer('Категория успешно удалена!', reply_markup=await kb.categories())
    await add_messages(callback.from_user.id, [sent_message.message_id])
    await delete_category(category_id)


@router.callback_query(F.data.startswith('product_up_'))
async def update_product(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    product_id = callback.data.split('_')[2]
    sent_message = await callback.message.answer('Обновление товара: ', reply_markup=kb.updating_product_keyboard(product_id))
    await add_messages(callback.from_user.id, [sent_message.message_id])

@router.callback_query(F.data.startswith('product_update'))
async def upgrade_product(callback: CallbackQuery, state: FSMContext):
    await remove_all_messages(callback.from_user.id, callback.bot)
    data = callback.data.split('_')
    product_id = data[-1]
    field_name = data[2].replace('-', '_')
    await state.set_state(ProductUpdateForm.new_value)
    await state.update_data(product_id=product_id, field_name=field_name)
    sent_message = await callback.message.answer('Введите новые данные: ')
    await add_messages(callback.from_user.id, [sent_message.message_id])

@router.message(ProductUpdateForm.new_value)
async def final_upgrage_order(message: Message, state: FSMContext):
    await remove_all_messages(message.from_user.id, message.bot)
    await state.update_data(new_value=message.text)
    data = await state.get_data()
    await state.clear()
    try:
        await update_product_field(**data)
    except ValueError:
        sent_message = await message.answer('Цена должна быть числом!', reply_markup=kb.main)
        await add_messages(message.from_user.id, [sent_message.message_id])
        return
    sent_message = await message.answer('Успешно обновлено!', reply_markup=kb.updating_product_keyboard(data.get('product_id')))
    await add_messages(message.from_user.id, [sent_message.message_id])

@router.callback_query(F.data.startswith('product_'))
async def product_detail(callback: CallbackQuery):
    await remove_all_messages(callback.from_user.id, callback.bot)
    product_id = callback.data.split('_')[1]
    product = await request_product(product_id)
    text = f"Наименование товара: {product.name}\n" \
           f"Цена товара: {product.price}\n" \
           f"Остаток товара: хз\n"
    
    sent_message = await callback.message.answer(text, reply_markup=await kb.delete_update_product(product_id))
    await add_messages(callback.from_user.id, [sent_message.message_id])