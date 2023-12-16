from pydantic import BaseModel

from ..pydanticutils import IS_PYDANTIC_V1
from .getters import DjangoGetter
from .mixins import SchemaMixins


class Schema(SchemaMixins, BaseModel):
    if IS_PYDANTIC_V1:

        class Config:
            orm_mode = True
            getter_dict = DjangoGetter

    else:
        model_config = {"from_attributes": True}
