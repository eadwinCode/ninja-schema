from pydantic import BaseModel

from ..pydanticutils import IS_PYDANTIC_V1
from .getters import DjangoGetter
from .mixins import SchemaMixins


class Schema(SchemaMixins, BaseModel):
    class Config:
        if IS_PYDANTIC_V1:
            orm_mode = True
            getter_dict = DjangoGetter
        else:
            from_attributes = True
