from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from models.pyd_items import Error
from utils.item_utils import ItemNotFoundError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(Error(code=400, message="Validation Failed"))
    )


async def not_found_exception_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content=jsonable_encoder(Error(code=404, message="Item not found"))
    )
