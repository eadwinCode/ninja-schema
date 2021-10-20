from typing import TYPE_CHECKING, List, Optional, Type, Union, cast

from django.db.models import Model

from ..errors import ConfigError
from ..types import DictStrAny
from .schema_registry import SchemaRegister, registry as schema_registry

if TYPE_CHECKING:
    from .model_schema import ModelSchema
    from .schema import Schema

__all__ = [
    "SchemaFactory",
]


class SchemaFactory:
    @classmethod
    def get_model_config(cls, **kwargs: DictStrAny) -> Type:
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
        registry: SchemaRegister = schema_registry,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        skip_registry: bool = False
    ) -> Union[Type["ModelSchema"], Type["Schema"], None]:
        from .model_schema import ModelSchema

        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set.")

        schema = registry.get_model_schema(model)
        if schema:
            return schema

        model_config_kwargs = dict(
            model=model,
            include=fields,
            exclude=exclude,
            skip_registry=skip_registry,
            depth=depth,
            registry=registry,
        )
        model_config = cls.get_model_config(**model_config_kwargs)  # type: ignore

        attrs = dict(Config=model_config)

        new_schema = type(name, (ModelSchema,), attrs)
        new_schema = cast(Type[ModelSchema], new_schema)
        if not skip_registry:
            registry.register_model(model, new_schema)
        return new_schema
