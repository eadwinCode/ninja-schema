import typing as t
import warnings

from django.db.models import Model as DjangoModel

from ..pydanticutils import IS_PYDANTIC_V1
from ..types import DictStrAny
from .getters import DjangoGetter

if not IS_PYDANTIC_V1:
    from pydantic import model_validator
    from pydantic.json_schema import GenerateJsonSchema
    from pydantic_core.core_schema import ValidationInfo

S = t.TypeVar("S", bound="Schema")


class SchemaMixins:
    def apply_to_model(
        self, model_instance: t.Type[DjangoModel], **kwargs: DictStrAny
    ) -> t.Type[DjangoModel]:
        for attr, value in self.dict(**kwargs).items():
            setattr(model_instance, attr, value)
        return model_instance

    if not IS_PYDANTIC_V1:

        @model_validator(mode="before")
        def _run_root_validator(cls, values: t.Any, info: ValidationInfo) -> t.Any:
            values = DjangoGetter(values, cls, info.context)
            return values

        @classmethod
        def from_orm(cls: t.Type[S], obj: t.Any, **options: t.Any) -> S:
            return cls.model_validate(obj, **options)

        def dict(self, *a: t.Any, **kw: t.Any) -> DictStrAny:
            # Backward compatibility with pydantic 1.x
            return self.model_dump(*a, **kw)

        @classmethod
        def json_schema(cls) -> DictStrAny:
            return cls.model_json_schema(schema_generator=GenerateJsonSchema)

        @classmethod
        def schema(cls) -> DictStrAny:
            warnings.warn(
                ".schema() is deprecated, use .json_schema() instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return cls.json_schema()
