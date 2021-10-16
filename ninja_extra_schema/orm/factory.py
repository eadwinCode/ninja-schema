from typing import Any, List, Optional, Tuple, Type, TYPE_CHECKING, cast

from django.db.models import Model
from ninja.errors import ConfigError
from .schema_registry import SchemaRegister

if TYPE_CHECKING:
    from .model_schema import ModelSchema

__all__ = ["SchemaFactory", ]


class SchemaFactory:
    @classmethod
    def get_model_config(cls, **kwargs):
        class Config:
            pass

        for key, value in kwargs.items():
            setattr(Config, key, value)
        return Config

    @classmethod
    def create_schema(
            cls,
            model: Type[Model],
            *,
            registry: SchemaRegister,
            name: str = "",
            depth: int = 0,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            skip_registry=False
    ) -> Type['ModelSchema']:
        from .model_schema import ModelSchema
        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set.")

        schema = registry.get_model_schema(model)
        if schema:
            return schema

        model_config = cls.get_model_config(
            model=model, include=fields, exclude=exclude, skip_registry=skip_registry,
            depth=depth, registry=registry,
        )

        attrs = dict(Config=model_config)

        new_schema = type(name, (ModelSchema,), attrs)
        new_schema = cast(Type[ModelSchema], new_schema)
        if not skip_registry:
            registry.register_model(model, new_schema)
        return new_schema
