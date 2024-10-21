import re
from fernet import Fernet
from pydantic import BaseModel, EmailStr, Field, constr, condecimal, field_validator, SecretStr
from enum import Enum
from typing import List, Optional, Annotated
from datetime import datetime
from pydantic_extra_types.phone_numbers import PhoneNumber
from src.config import settings

# store and DO NOT lost this fernet_key = Fernet.generate_key()
fernet = Fernet(settings.ENCRYPTION_KEY)

class Customer(BaseModel):
    first_name: str
    last_name: str
    email: SecretStr
    address: str
    
    @field_validator('address')
    def encrypt_address(cls, v):
        pass
    
    