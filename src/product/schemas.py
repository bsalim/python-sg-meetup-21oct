import re
from datetime import datetime
from pydantic import EmailStr, Field, field_validator, HttpUrl, UUID4

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")

from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional

class ProductRequest(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    availability: bool
    image: HttpUrl
    ratings: Optional[float] = 0
    discount: Optional[float] = 0
    manufacturer: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = []


# Pydantic model for Product (Response Model)
class ProductResponse(ProductRequest):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None