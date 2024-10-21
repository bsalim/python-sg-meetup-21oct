from src.pydantic_extras.schema import PaymentCardExample
from src.pydantic_extras.schema import PendulumExample

payment = PaymentCardExample(card_number='1234578', card_brand='Visaaa')

datetime_test = PendulumExample(date_string='2024')