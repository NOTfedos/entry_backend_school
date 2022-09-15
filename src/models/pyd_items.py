from __future__ import annotations
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
import iso8601

from .db_items import SystemItemType


class SystemItemImport(BaseModel):
    id: str
    url: str | None = Field(default=None)
    parent_id: str | None = Field(default=None, alias="parentId")
    itemtype: SystemItemType = Field(..., alias="type")
    size: int | None = None

    class Config:
        schema_extra = {
            "example": {
                "id": "элемент_1_4",
                "url": "/file/url1",
                "parentId": "элемент_1_1",
                "size": 234,
                "type": "FILE"
            }
        }
        validate_assignment = True

    @root_validator
    def validate_url(cls, values):

        if values['id'] is None:
            raise ValueError

        # logging.debug(values)
        if (values['url'] is not None) and len(values['url']) > 255:
            raise ValueError

        if values['itemtype'] == 'FOLDER':
            if values['url'] is not None:
                raise ValueError
            if values['size'] is not None:
                raise ValueError
            else:
                # Set size to 0 for FOLDER
                values['size'] = 0
        if values['itemtype'] == 'FILE':
            if values['url'] is None:
                raise ValueError
            if values['size'] is None:
                raise ValueError
            else:
                if values['size'] <= 0:
                    raise ValueError
        return values


class SystemItemGetNode(BaseModel):
    id: str
    url: str | None = Field(default=None)
    parent_id: str | None = Field(default=None, alias="parentId")
    itemtype: SystemItemType = Field(..., alias="type")
    size: int | None
    date: datetime
    children: list[SystemItemGetNode] | None = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


class SystemItemImportRequest(BaseModel):
    items: list[SystemItemImport]
    update_date: datetime = Field(..., alias="updateDate")

    # class Config:
    #     json_encoders = {
    #         datetime: lambda v: iso8601.parse_date(v),
    #     }

    @validator('update_date', pre=True)
    def time_validate(cls, v):
        return iso8601.parse_date(v)

    class Config:
        schema_extra = {
            "example": {
                "updateDate": "2022-05-28T21:12:01.000Z"
            }
        }


class SystemItemHistoryResponse(BaseModel):
    items: list[SystemItemHistoryUnit] = []


class SystemItemHistoryUnit(BaseModel):
    id: str
    url: str | None = None
    parent_id: str | None = Field(None, alias="parentID")
    itemtype: SystemItemType = Field(..., alias="type")
    size: int | None = None
    date: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    # @root_validator
    # def validate_date(cls, values):
    #     values['date'] = iso8601.parse_date(values['date'].isoformat())
    #     return values


class Error(BaseModel):
    code: int
    message: str

    class Config:
        schema_extra = {
            "example": {
                "code": "400",
                "message": "Validation Failed"
            }
        }


SystemItemHistoryResponse.update_forward_refs()
SystemItemGetNode.update_forward_refs()
