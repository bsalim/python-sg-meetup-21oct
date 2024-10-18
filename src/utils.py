import logging
import random
import string
from decimal import Decimal

from fastapi import Request
from jinja2 import Environment, FileSystemLoader

from src.config import settings

logger = logging.getLogger(__name__)

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


# Utility functions for flash messages
def set_flash_message(request: Request, message: str, category: str):
    request.session["flash"] = {"message": message, "category": category}

def get_flash_message(request: Request):
    message = request.session.pop("flash", None)
    return message

def get_presigned_url():
    pass

# def send_email(to_email: str, subject: str, template_file: str, context: dict = {}) -> object:
#     try:
#         template_loader = FileSystemLoader('templates')
#         template_env = Environment(loader=template_loader)
#         template = template_env.get_template(template_file)
#         html_content = template.render(context)
#     except Exception as err:
#         logger.error(f'Error loading or rendering template: {err}')
#         raise

#     # Configure Resend
#     try:
#         resend.api_key = settings.RESEND_API_KEY
#     except AttributeError as err:
#         logger.error(f"API Key configuration error: {err}")
#         raise

#     # Prepare email parameters
#     params = {
#         "from": "Info <info@ibupedia.com>",
#         "to": [to_email],
#         "subject": subject,
#         "html": html_content
#     }

#     # Send the email
#     try:
#         response = resend.Emails.send(params)
#         logger.info(f'Email sent successfully to {to_email}. Response: {response}')
#     except Exception as err:
#         logger.error(f'Error sending email: {err}')
#         raise


def convert_decimal_to_cents(amount: Decimal) -> int:
    # Ensure the amount is rounded to 2 decimal places and converted to integer cents
    return int(amount * 100)
