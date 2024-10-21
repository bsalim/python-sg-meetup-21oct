from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.product.router import router as product_router
from src.payment.router import router as payment_router

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.get('/healthcheck', include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(product_router)
app.include_router(payment_router)