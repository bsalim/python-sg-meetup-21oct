from pydantic import BaseModel
from pydantic_extra_types.currency_code import Currency
from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber
from pydantic_extra_types.pendulum_dt import Date
from pydantic_extra_types.timezone_name import TimeZoneName


class PaymentCardExample(BaseModel):
    card_number: PaymentCardNumber
    card_brand: PaymentCardBrand


class PendulumExample(BaseModel):
    date_string: Date

    
class TimezoneExample(BaseModel):
    tz: TimeZoneName

    
class CurrencyExample(BaseModel):
    code: Currency