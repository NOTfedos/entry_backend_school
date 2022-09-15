# Import libs
import iso8601
from fastapi import Depends, Query, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from sqlalchemy.ext.asyncio import AsyncSession

# Import modules
from models.pyd_items import SystemItemImport, SystemItemImportRequest, \
    SystemItemGetNode, SystemItemHistoryResponse, Error
from utils.db import get_session
from utils.item_utils import import_items, delete_item, get_nodes, get_recent_updated_files, get_item_history_db

item_router = InferringRouter()


@cbv(item_router)
class ItemCBV:
    session: AsyncSession = Depends(get_session)

    @item_router.post("/imports",
                      tags=["Базовые задачи"],
                      description="Импортирует элементы файловой системы. Элементы импортированные повторно обновляют текущие.",
                      responses={
                          200: {"description": "Вставка или обновление прошли успешно."},
                          400: {"description": "Невалидная схема документа или входные данные не верны.",
                                "model": Error}
                      },
                      )
    async def import_items(self, items_request: SystemItemImportRequest):
        # Import to DB
        await import_items(self.session, items_request)
        return Response(status_code=200)

    @item_router.delete("/delete/{id}",
                        tags=["Базовые задачи"],
                        description="Удалить элемент по идентификатору. При удалении папки удаляются все дочерние элементы.",
                        responses={
                            200: {"description": "Удаление прошло успешно."},
                            400: {"description": "Невалидная схема документа или входные данные не верны.",
                                  "model": Error},
                            404: {"description": "Элемент не найден.",
                                  "model": Error}
                        },
                        )
    async def delete_item(self, id: str, date: str = Query(..., example="2022-05-28T21:12:01.516Z")):
        # Try out to parse datetime
        try:
            date = iso8601.parse_date(date)
        except ValueError:
            return JSONResponse(status_code=400, content=jsonable_encoder(Error(code=400, message="Validation Failed")))

        # Delete items from DB
        await delete_item(self.session, id, date)
        return Response(status_code=200)

    @item_router.get("/nodes/{id}",
                     tags=["Базовые задачи"],
                     description="Получить информацию об элементе по идентификатору.",
                     responses={
                         200: {"description": "Информация об элементе.",
                               "model": SystemItemGetNode},
                         400: {"description": "Невалидная схема документа или входные данные не верны.",
                               "model": Error},
                         404: {"description": "Элемент не найден.",
                               "model": Error}
                     },
                     )
    async def get_nodes(self, id: str) -> SystemItemGetNode:
        return await get_nodes(self.session, id)

    @item_router.get("/updates",
                     tags=["Дополнительные задачи"],
                     description="Получение списка **файлов**, которые были обновлены за последние 24 часа",
                     responses={
                         200: {"description": "Список элементов, которые были обновлены.",
                               "model": SystemItemHistoryResponse},
                         400: {"description": "Невалидная схема документа или входные данные не верны.",
                               "model": Error},
                     },
                     )
    async def get_updated_items(self, date: str = Query(...)):
        # Try out to parse datetime
        try:
            date = iso8601.parse_date(date)
        except ValueError:
            return JSONResponse(status_code=400, content=jsonable_encoder(Error(code=400, message="Validation Failed")))

        return await get_recent_updated_files(self.session, date)

    @item_router.get("/node/{id}/history",
                     tags=["Дополнительные задачи"],
                     description="Получение истории обновлений по элементу за заданный полуинтервал [from, to).",
                     responses={
                         200: {"description": "История по элементу.",
                               "model": SystemItemHistoryResponse},
                         400: {"description": "Невалидная схема документа или входные данные не верны.",
                               "model": Error},
                         404: {"description": "Элемент не найден.",
                               "model": Error}
                     },
                     )
    async def get_item_history(self, id: str,
                               date_start: str = Query(None, alias="dateStart"),
                               date_end: str = Query(None, alias="dateEnd")
                               ):
        # Try out to parse datetime
        try:
            date_start = iso8601.parse_date(date_start)
            date_end = iso8601.parse_date(date_end)
        except ValueError:
            return JSONResponse(status_code=400, content=jsonable_encoder(Error(code=400, message="Validation Failed")))

        return await get_item_history_db(self.session, id, date_start, date_end)
