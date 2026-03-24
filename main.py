from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.operations import add, subtract, multiply, divide

import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error("HTTPException on %s: %s", request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_messages = "; ".join(f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors())
    logger.error("ValidationError on %s: %s", request.url.path, error_messages)
    return JSONResponse(status_code=400, content={"error": error_messages})


@app.get("/")
async def read_root(request: Request):
    """Render the homepage."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """Return the sum of two numbers."""
    try:
        return OperationResponse(result=add(operation.a, operation.b))
    except Exception as exc:
        logger.error("Add operation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """Return the difference of two numbers."""
    try:
        return OperationResponse(result=subtract(operation.a, operation.b))
    except Exception as exc:
        logger.error("Subtract operation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """Return the product of two numbers."""
    try:
        return OperationResponse(result=multiply(operation.a, operation.b))
    except Exception as exc:
        logger.error("Multiply operation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """Return the quotient of two numbers."""
    try:
        return OperationResponse(result=divide(operation.a, operation.b))
    except ValueError as exc:
        logger.error("Divide operation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Divide operation internal error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
