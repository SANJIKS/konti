from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

TOKEN = "8095877313:AAGeO_Pc6nGoKIou0AusHAkdE7r6Q20219E"
DATABASE_URL = "postgres://sanjik:1@localhost:5432/konti_db"

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, nullable=False)

    stock_in_records = relationship("StockIn", back_populates="product")
    stock_out_records = relationship("StockOut", back_populates="product")

class StockIn(Base):
    __tablename__ = 'stock_in'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    product = relationship("Product", back_populates="stock_in_records")

class StockOut(Base):
    __tablename__ = 'stock_out'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    product = relationship("Product", back_populates="stock_out_records")

Base.metadata.create_all(bind=engine)

# Bot setup
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Helpers
def get_session():
    return SessionLocal()

# Handlers
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Добро пожаловать! Используйте команды: \n/add_product \n/stock_in \n/stock_out \n/check_stock")

@router.message(Command("add_product"))
async def add_product(message: Message):
    try:
        _, name, price = message.text.split(maxsplit=2)
        price = float(price)
        session = get_session()
        if session.query(Product).filter_by(name=name).first():
            await message.answer(f"Товар '{name}' уже существует.")
        else:
            product = Product(name=name, price=price)
            session.add(product)
            session.commit()
            await message.answer(f"Товар '{name}' успешно добавлен с ценой {price}.")
    except ValueError:
        await message.answer("Использование: /add_product [название_товара] [цена]")
    finally:
        session.close()

@router.message(Command("stock_in"))
async def stock_in(message: Message):
    try:
        _, name, quantity, price = message.text.split(maxsplit=3)
        quantity = int(quantity)
        price = float(price)
        session = get_session()
        product = session.query(Product).filter_by(name=name).first()
        if product:
            product.quantity += quantity
            stock_in_record = StockIn(product_id=product.id, quantity=quantity, price=price)
            session.add(stock_in_record)
            session.commit()
            await message.answer(f"Поступило {quantity} шт. товара '{name}' по цене {price}. Текущий остаток: {product.quantity}.")
        else:
            await message.answer(f"Товар '{name}' не найден.")
    except ValueError:
        await message.answer("Использование: /stock_in [название_товара] [количество] [цена]")
    finally:
        session.close()

@router.message(Command("stock_out"))
async def stock_out(message: Message):
    try:
        _, name, quantity, price = message.text.split(maxsplit=3)
        quantity = int(quantity)
        price = float(price)
        session = get_session()
        product = session.query(Product).filter_by(name=name).first()
        if product:
            if product.quantity >= quantity:
                product.quantity -= quantity
                stock_out_record = StockOut(product_id=product.id, quantity=quantity, price=price)
                session.add(stock_out_record)
                session.commit()
                await message.answer(f"Списано {quantity} шт. товара '{name}' по цене {price}. Текущий остаток: {product.quantity}.")
            else:
                await message.answer(f"Недостаточно товара '{name}' на складе. Текущий остаток: {product.quantity}.")
        else:
            await message.answer(f"Товар '{name}' не найден.")
    except ValueError:
        await message.answer("Использование: /stock_out [название_товара] [количество] [цена]")
    finally:
        session.close()

@router.message(Command("check_stock"))
async def check_stock(message: Message):
    session = get_session()
    products = session.query(Product).all()
    if products:
        stock_info = "Текущий остаток:\n"
        for product in products:
            stock_info += f"{product.name}: {product.quantity} шт., цена: {product.price}\n"
        await message.answer(stock_info)
    else:
        await message.answer("На складе нет товаров.")
    session.close()

if __name__ == "__main__":
    import asyncio

    asyncio.run(dp.start_polling(bot))
