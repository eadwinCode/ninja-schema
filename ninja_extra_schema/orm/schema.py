from django.core.paginator import Page
from django.db import models
from django.db.models import QuerySet
from typing import Any

import pydantic
from django.db.models import Manager, QuerySet
from django.db.models.fields.files import FieldFile
from pydantic import BaseModel, Field, validator
from pydantic.utils import GetterDict

pydantic_version = list(map(int, pydantic.VERSION.split(".")))[:2]
assert pydantic_version >= [1, 6], "Pydantic 1.6+ required"

__all__ = ["BaseModel", "Field", "validator", "DjangoGetter", "Schema"]


class DjangoGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        result = super().get(key, default)

        if isinstance(result, Manager):
            return list(result.all())

        elif isinstance(result, QuerySet):
            return list(result)

        elif isinstance(result, FieldFile):
            if not result:
                return None
            return result.url

        return result


class Schema(BaseModel):
    class Config:
        orm_mode = True
        getter_dict = DjangoGetter

    def apply(self, model_instance: models.Model, **kwargs):
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance

    @classmethod
    def from_django(cls, model_instance, many=False):
        if many:
            if isinstance(model_instance, (QuerySet, list, Page)):
                return [cls.from_orm(model) for model in model_instance]
            raise Exception('model_instance must a queryset or list')
        return cls.from_orm(model_instance)
