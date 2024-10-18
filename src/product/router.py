from faker import Faker
from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
from src.database import get_db
from src.product.models import Product, Category
from src.product.schemas import ProductSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select

router = APIRouter(prefix="")


@router.get("/products", response_model=list[ProductSchema])


from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@router.get("/insert_products")
async def insert_products(db: AsyncSession = Depends(get_db)):
    fake = Faker()
    products = [Product(name=fake.word(), price=100) for _ in range(1_000_000)]
    
    try:
        async with db.begin():
            db.add_all(products)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "1 million products inserted successfully"}