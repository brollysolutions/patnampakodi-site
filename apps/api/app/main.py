from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.commerce_api import router
from app.content import storefront
from app.db import content_connection
from app.schemas import Health, Product, Storefront

app = FastAPI(
    title="Patnam Pakodi Content API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
Connection = Annotated[psycopg.AsyncConnection, Depends(content_connection)]
app.include_router(router)


@app.middleware("http")
async def bounded_body(request, call_next):
    maximum = 5_000_000 if request.url.path == "/v1/admin/media" else 1_000_000
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > maximum:
            return JSONResponse(status_code=413, content={"detail": "Request is too large"})
    request._body = bytes(body)
    return await call_next(request)


@app.exception_handler(psycopg.errors.UniqueViolation)
@app.exception_handler(psycopg.errors.CheckViolation)
async def invalid_change(_request, _exception):
    return JSONResponse(
        status_code=409,
        content={"detail": "This change conflicts with an existing record or constraint"},
    )


@app.middleware("http")
async def private_api_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(psycopg.Error)
@app.exception_handler(ValidationError)
@app.exception_handler(RuntimeError)
async def content_unavailable(_request, _exception):
    # Never serialize database errors, connection strings or invalid draft values.
    return JSONResponse(status_code=503, content={"detail": "Content is temporarily unavailable"})


@app.get("/health", response_model=Health, operation_id="health")
async def health(connection: Connection) -> Health:
    await connection.execute("SELECT 1")
    return Health()


@app.get("/v1/storefront", response_model=Storefront, operation_id="getStorefront")
async def get_storefront(connection: Connection) -> Storefront:
    return await storefront(connection)


@app.get("/v1/products/{slug}", response_model=Product, operation_id="getProduct")
async def get_product(slug: str, connection: Connection) -> Product:
    content = await storefront(connection)
    product = next((item for item in content.products if item.slug == slug), None)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product
