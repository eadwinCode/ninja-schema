from typing import TYPE_CHECKING, Callable, List, Type, Union

from django.core.paginator import Page
from django.db.models import Model as DjangoModel, QuerySet

from ..types import DictStrAny

if TYPE_CHECKING:
    from pydantic.main import BaseModel


class SchemaMixins:
    dict: Callable

    def apply_to_model(
        self, model_instance: Type[DjangoModel], **kwargs: DictStrAny
    ) -> Type[DjangoModel]:
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance

    @classmethod
    def from_django(
        cls, model_instance: Union[QuerySet, Page, DjangoModel], many: bool = False
    ) -> Union[Type["BaseModel"], List[Type["BaseModel"]]]:
        if many:
            if isinstance(model_instance, (QuerySet, list, Page)):
                return [cls.from_orm(model) for model in model_instance]  # type: ignore
            raise Exception("model_instance must a queryset or list")
        return cls.from_orm(model_instance)  # type: ignore
