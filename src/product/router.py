from uuid import uuid4
from datetime import datetime
from faker import Faker
from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from src.product.schemas import ProductRequest, ProductResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import joinedload
# from sqlalchemy import select

router = APIRouter(prefix="")


@router.post("/product", response_model=ProductResponse)
async def create_product(request: Request, product: ProductRequest):
    # Create the product instance
    product_response = ProductResponse(
        **product.model_dump(),
        id=uuid4(),
        created_at=datetime.now(),
    )
    return product_response
    

# @router.get("/insert_products")
# async def insert_products(db: AsyncSession = Depends(get_db)):
#     fake = Faker()
#     products = [Product(name=fake.word(), price=100) for _ in range(1_000_000)]
    
#     try:
#         async with db.begin():
#             db.add_all(products)
#         await db.commit()
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
    
#     return {"message": "1 million products inserted successfully"}