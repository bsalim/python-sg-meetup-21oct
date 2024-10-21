import logging
from uuid import uuid4
from datetime import datetime
from faker import Faker
from fastapi import FastAPI, APIRouter, Depends, status, UploadFile, Request, HTTPException
from src.payment.schema import PaymentRequest, PaymentResponse, TransactionStatus

router = APIRouter(prefix="/payment")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/card", response_model=PaymentResponse)
async def create_payment(request: Request, product: PaymentRequest):
    # Generate a new unique transaction ID

    # Log the masked card number (first 4 digits and last 4 digits, others hidden)
    logger.info(f"Processing payment with card {product.masked_card_number}")

    transaction_status = TransactionStatus.SUCCESS

    # Create the response
    payment_response = PaymentResponse(
        transaction_id=uuid4(),
        amount=product.amount,
        card_brand=product.card_brand,
        cvv=product.cvv.get_secret_value(),
        masked_card_number=product.masked_card_number,
        transaction_status=transaction_status,
        timestamp=datetime.now()
    )

    return payment_response

