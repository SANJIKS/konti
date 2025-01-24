from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_products, get_products_by_category, stock_in_request, stock_out_request


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Товары')], 
    [KeyboardButton(text='Приход')],
    [KeyboardButton(text='Уход')],
    [KeyboardButton(text='Остаток')]
], resize_keyboard=True)


add_product = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить товар')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_stock_in = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить приход')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_stock_out = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить уход')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_product_detail = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Товары')], 
    [KeyboardButton(text='Добавить товар')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_stock_in_detail = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Приход')],
    [KeyboardButton(text='Добавить приход')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_stock_out_detail = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Уход')],
    [KeyboardButton(text='Добавить уход')], 
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)

add_category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить категорию')],
    [KeyboardButton(text='Удалить категорию')],
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начало работы')
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def products(category_id):
    products_kb = InlineKeyboardBuilder()
    products = await get_products_by_category(category_id)
    for product in products:
        products_kb.add(InlineKeyboardButton(text=product.name, callback_data=f'product_{product.id}'))
    return products_kb.adjust(2).as_markup()

async def categories():
    categories_kb = InlineKeyboardBuilder()
    categories = await get_categories()
    for category in categories:
        categories_kb.add(InlineKeyboardButton(text=category.name, callback_data=f'products_cg_{category.id}'))
    return categories_kb.adjust(2).as_markup()

async def categories_list():
    categories_kb = InlineKeyboardBuilder()
    categories = await get_categories()
    for category in categories:
        categories_kb.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    return categories_kb.adjust(2).as_markup()

async def categories_for_del():
    categories_kb = InlineKeyboardBuilder()
    categories = await get_categories()
    for category in categories:
        categories_kb.add(InlineKeyboardButton(text=category.name, callback_data=f'category_rm_{category.id}'))
    return categories_kb.adjust(2).as_markup()

async def stock_ins():
    stock_ins_kb = InlineKeyboardBuilder()
    stocks_ins = await stock_in_request()
    for stock_in in stocks_ins:
        formatted_date = stock_in.timestamp.strftime("%d-%m-%Y %H:%M:%S")
        stock_ins_kb.add(InlineKeyboardButton(
            text=f"Приход №{stock_in.id} - {formatted_date}", 
            callback_data=f'stock_in_{stock_in.id}')
        )
    return stock_ins_kb.adjust(2).as_markup()

async def stock_out():
    stock_outs_kb = InlineKeyboardBuilder()
    stocks_outs = await stock_out_request()
    for stock_out in stocks_outs:
        formatted_date = stock_out.timestamp.strftime("%d-%m-%Y %H:%M:%S")
        stock_outs_kb.add(InlineKeyboardButton(
            text=f"Уход №{stock_out.id} - {formatted_date}", 
            callback_data=f'stock_out_{stock_out.id}')
        )
    return stock_outs_kb.adjust(2).as_markup()


async def products_for_stock():
    products_kb = InlineKeyboardBuilder()
    products = await get_products()
    for product in products:
        products_kb.add(InlineKeyboardButton(text=product.name, callback_data=f'pr_to_si_{product.id}'))
    return products_kb.adjust(2).as_markup()


async def delete_update_product(product_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Обновить', callback_data=f'product_up_{product_id}')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'product_rm_{product_id}')]
    ])
    return keyboard

async def delete_update_stock_in(stock_in_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить', callback_data=f'stock_in_rm_{stock_in_id}')]
    ])
    return keyboard

async def delete_update_stock_out(stock_out_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить', callback_data=f'stock_out_rm_{stock_out_id}')]
    ])
    return keyboard
    


# def create_delete_product_keyboard(product_id):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text="Удалить товар", callback_data=f"delete_product_{product_id}"))
#     return keyboard.adjust(2).as_markup()



# async def successful_orders():
#     orders = await get_successful_orders()
#     orders_kb = InlineKeyboardBuilder()
#     for order in orders:
#         orders_kb.add(InlineKeyboardButton(text=f'ID: {order.id}\nPhone: {order.customer_phone}', callback_data=f'the_order_{order.id}'))
#     return orders_kb.adjust(2).as_markup()


# async def false_orders():
#     orders = await get_orders()
#     orders_kb = InlineKeyboardBuilder()
#     for order in orders:
#         orders_kb.add(InlineKeyboardButton(text=f'ID: {order.id}\nPhone: {order.customer_phone}', callback_data=f'the_order_{order.id}'))
#     return orders_kb.adjust(2).as_markup()


# def update_delete_order_keyboard(order_id):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text="Удалить заказ", callback_data=f"delete_order_{order_id}"))
#     keyboard.add(InlineKeyboardButton(text='Редактировать заказ', callback_data=f'update_order_{order_id}'))
#     return keyboard.adjust(2).as_markup()


def updating_product_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Наименование товара', callback_data=f'product_update_name_{product_id}')],
        [InlineKeyboardButton(text='Цена', callback_data=f'product_update_price_{product_id}')]
    ])
    return keyboard