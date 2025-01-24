from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload
from app.database.models import Category, Product, async_session, StockIn, StockOut

async def get_products():
    async with async_session() as session:
        result = await session.scalars(select(Product))
        return result

async def get_categories():
    async with async_session() as session:
        result = await session.scalars(select(Category))
        return result

async def stock_in_request():
    async with async_session() as session:
        result = await session.scalars(select(StockIn))
        return result

async def stock_out_request():
    async with async_session() as session:
        result = await session.scalars(select(StockOut))
        return result

async def stock_in_detail_request(stock_in_id):
    async with async_session() as session:
        result = await session.scalar(select(StockIn).options(joinedload(StockIn.product)).where(StockIn.id == int(stock_in_id)))
        return result

async def stock_out_detail_request(stock_out_id):
    async with async_session() as session:
        result = await session.scalar(select(StockOut).options(joinedload(StockOut.product)).where(StockOut.id == int(stock_out_id)))
        return result


async def request_product(product_id):
    async with async_session() as session:
        result = await session.scalar(select(Product).where(Product.id == int(product_id)))
        return result

async def get_products_by_category(category_id):
    async with async_session() as session:
        result = await session.scalars(
            select(Product).where(Product.category_id == int(category_id))
        )
        return result


async def create_product(category_id, name, price):
    async with async_session() as session:
        product = Product(
            category_id=int(category_id),
            name=name,
            price=price
        )
        session.add(product)
        await session.commit()
    
async def create_category(name):
    async with async_session() as session:
        category = Category(
            name=name
        )
        session.add(category)
        await session.commit()

async def delete_product(product_id):
    async with async_session() as session:
        deleted_product = delete(Product).where(Product.id == int(product_id))
        await session.execute(deleted_product)
        await session.commit()

async def delete_stock_in(stock_in_id):
    async with async_session() as session:
        deleted_stock_in = delete(StockIn).where(StockIn.id == int(stock_in_id))
        await session.execute(deleted_stock_in)
        await session.commit()

async def delete_stock_out(stock_out_id):
    async with async_session() as session:
        deleted_stock_out = delete(StockOut).where(StockOut.id == int(stock_out_id))
        await session.execute(deleted_stock_out)
        await session.commit()

async def delete_category(category_id):
    async with async_session() as session:
        deleted_category = delete(Category).where(Category.id ==int(category_id))
        await session.execute(deleted_category)
        await session.commit()


async def update_product_field(product_id, field_name, new_value):
    try:
        if field_name == "price":
            new_value = float(new_value)

        async with async_session() as session:
            await session.execute(
                update(Product)
                .where(Product.id == int(product_id))
                .values({field_name: new_value})
            )
            await session.commit()
    except ValueError:
        raise ValueError(f"Неверный формат значения для поля '{field_name}'.")


async def create_stock_in(product_id, quantity):
    async with async_session() as session:
        stock_in = StockIn(
            product_id=int(product_id),
            quantity=quantity
        )
        session.add(stock_in)
        await session.commit()


async def create_stock_out(product_id, quantity):
    async with async_session() as session:
        stock_out = StockOut(
            product_id=int(product_id),
            quantity=quantity
        )
        session.add(stock_out)
        await session.commit()


async def stock():
    async with async_session() as session:
        results = await session.execute(
            select(
                Product.id,
                Product.name,
                (func.coalesce(func.sum(StockIn.quantity), 0) - func.coalesce(func.sum(StockOut.quantity), 0)).label('balance')
            )
            .join(StockIn, StockIn.product_id == Product.id, isouter=True)
            .join(StockOut, StockOut.product_id == Product.id, isouter=True)
            .group_by(Product.id, Product.name)
            .order_by(Product.name)
        )
        return results.all()
    

async def get_product_balance(product_id: int):
    product_id = int(product_id)
    async with async_session() as session:
        result = await session.execute(
            select(
                Product.id,
                Product.name,
                (func.coalesce(func.sum(StockIn.quantity), 0) - func.coalesce(func.sum(StockOut.quantity), 0)).label('balance')
            )
            .join(StockIn, StockIn.product_id == Product.id, isouter=True)
            .join(StockOut, StockOut.product_id == Product.id, isouter=True)
            .filter(Product.id == product_id)
            .group_by(Product.id, Product.name)
        )
        balance = result.scalar_one_or_none()
        return balance