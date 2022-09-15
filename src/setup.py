from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_restful import Api

import logging
from aiomisc.log import basic_config

from controller.items import item_router
from controller.exc_handlers import validation_exception_handler, not_found_exception_handler
from utils.item_utils import ItemNotFoundError
from config import get_settings


def init_app():
    if get_settings().debug:
        basic_config(logging.DEBUG, buffered=True)
    else:
        basic_config(logging.INFO, buffered=True)
    # logging.basicConfig(level=logging.DEBUG)
    # logger = logging.getLogger(__name__)

    # Init app and api
    app = FastAPI()
    api = Api(app)

    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ItemNotFoundError, not_found_exception_handler)

    # Add routers
    app.include_router(item_router)

    return app
