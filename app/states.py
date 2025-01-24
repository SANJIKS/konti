from aiogram.fsm.state import State, StatesGroup

class ProductCreateForm(StatesGroup):
    category = State()
    name = State()
    price = State()


class ProductUpdateForm(StatesGroup):
    new_value = State()


class StockInCreateForm(StatesGroup):
    product = State()
    quantity = State()


class StockOutCreateForm(StatesGroup):
    product = State()
    quantity = State()

class CategoryCreateForm(StatesGroup):
    name = State()