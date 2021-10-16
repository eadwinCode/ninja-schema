from pydantic import BaseModel, Field, validator
from .getters import DjangoGetter


class Schema(BaseModel):
    class Config:
        orm_mode = True
        getter_dict = DjangoGetter
