from typing import Callable

from django.core.paginator import Page
from django.db.models import Model, QuerySet


class SchemaMixins:
    from_orm: Callable
    dict: Callable

    def apply_to_model(self, model_instance: Model, **kwargs):
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance

    @classmethod
    def from_django(cls, model_instance, many=False):
        if many:
            if isinstance(model_instance, (QuerySet, list, Page)):
                return [cls.from_orm(model) for model in model_instance]
            raise Exception("model_instance must a queryset or list")
        return cls.from_orm(model_instance)
