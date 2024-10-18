import re
from pydantic import BaseModel, EmailStr, Field, constr, condecimal, field_validator
from enum import Enum
from typing import List, Optional, Annotated
from datetime import datetime

# ENUM  for Order Status
class OrderStatus(str, Enum):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'

# ENUM for Payment Method
class PaymentMethod(str, Enum):
    CREDIT_CARD = 'Credit Card'
    PAYPAL = 'PayPal'
    BANK_TRANSFER = 'Bank Transfer'
    CASH_ON_DELIVERY = 'Cash on Delivery'

# Customer Information
class Customer(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] # Simple phone number regex
    shipping_address: str = Field(..., min_length=5)
    
    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        # Regex pattern to match a phone number starting with + followed by digits (between 10 and 15 digits after the +)
        pattern = re.compile(r'^\+?[1-9]\d{9,14}$')
        
        if not pattern.match(v):
            raise ValueError('Phone number must start with + and contain 10 to 15 digits')
        
        return v

# Product Information
class Product(BaseModel):
    product_id: str
    name: str
    quantity: int = Field(..., ge=1)
    price_per_unit: condecimal(max_digits=10, decimal_places=2)

# Shipment Information
class Shipment(BaseModel):
    shipment_id: str
    carrier: str
    tracking_number: Optional[str]
    shipment_date: Optional[datetime]
    estimated_delivery_date: Optional[datetime]

# Main Order Model
class Order(BaseModel):
    order_id: str
    customer: Customer
    products: List[Product]
    order_date: datetime
    status: OrderStatus
    payment_method: PaymentMethod
    total_amount: condecimal(max_digits=12, decimal_places=2)
    shipment: Optional[Shipment]
    note: Optional[str] = Field(None, max_length=500)

    # Calculate the total amount for the order
    def calculate_total(self) -> None:
        self.total_amount = sum([p.quantity * p.price_per_unit for p in self.products])

    # Custom validation for order status transitions
    @classmethod
    def validate_status_transition(cls, old_status: OrderStatus, new_status: OrderStatus):
        if old_status == OrderStatus.CANCELED:
            raise ValueError("Cannot update a canceled order.")
        if old_status == OrderStatus.DELIVERED and new_status != old_status:
            raise ValueError("Delivered orders cannot change status.")