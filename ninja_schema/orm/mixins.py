from typing import Callable, Type

from django.db.models import Model as DjangoModel

from ..types import DictStrAny


class SchemaMixins:
    dict: Callable

    def apply_to_model(
        self, model_instance: Type[DjangoModel], **kwargs: DictStrAny
    ) -> Type[DjangoModel]:
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance
