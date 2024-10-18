import re

from pydantic import EmailStr, Field, field_validator

from src.models import CustomModel

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")

from pydantic import BaseModel, ConfigDict, model_validator

class CategorySchema(BaseModel):
    id: int
    category_name: str

    class Config:
        orm_mode = True


class ProductSchema(BaseModel):
    name: str
    description: str
    category_name: str
    
    class Config:
        orm_mode = True