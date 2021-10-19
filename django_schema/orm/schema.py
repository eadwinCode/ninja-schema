from pydantic import BaseModel

from .getters import DjangoGetter
from .mixins import SchemaMixins


class Schema(BaseModel, SchemaMixins):
    class Config:
        orm_mode = True
        getter_dict = DjangoGetter
