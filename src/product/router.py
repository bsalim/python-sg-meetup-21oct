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
    