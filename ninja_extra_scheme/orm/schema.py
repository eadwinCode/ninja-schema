from django.core.paginator import Page
from django.db import models
from django.db.models import QuerySet
from ninja import Schema as NinjaSchema

__all__ = ['Schema', ]


class Schema(NinjaSchema):
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
