from datetime import datetime
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, SecretStr, Field, field_validator, UUID4
from pydantic_extra_types.payment import PaymentCardNumber

class TransactionStatus(Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"
    CANCELED = "Canceled"


class PaymentRequest(BaseModel):
    card_number: PaymentCardNumber = Field(
        ...,
        example="4111111111111111",  # Example Visa card number
        description="Valid Visa card number"
    )
    expiration_date: str 
    cvv: SecretStr
    amount: float
    cardholder_name: str 

    @property
    def card_brand(self) -> str:
        """Determine the card brand based on the card number."""
        card_number = self.card_number
        if card_number.startswith("4"):
            return "VISA"
        elif card_number.startswith("5"):
            return "MasterCard"
        else:
            return "Unknown"
        
    @property
    def masked_card_number(self) -> str:
        """Mask the card number, leaving only the first 4 and last 4 digits visible."""
        card_number = str(self.card_number)
        return f"{card_number[:4]} **** **** {card_number[-4:]}"


class PaymentResponse(BaseModel):
    transaction_id: UUID4
    amount: float
    card_brand: str
    cvv: str
    masked_card_number: str
    transaction_status: TransactionStatus  # Using Enum for transaction status
    timestamp: datetime
