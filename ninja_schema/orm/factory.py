import typing
from typing import TYPE_CHECKING, List, Optional, Type, Union, cast

from django.db.models import Model

from ninja_schema.errors import ConfigError
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from ninja_schema.types import DictStrAny

from .schema_registry import SchemaRegister
from .schema_registry import registry as schema_registry

if TYPE_CHECKING:
    from .model_schema import ModelSchema
    from .schema import Schema

__all__ = ["SchemaFactory"]


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
        skip_registry: bool = False,
        optional_fields: Optional[Union[str, List[str]]] = None,
        **model_config_options: DictStrAny,
    ) -> Union[Type["ModelSchema"], Type["Schema"], None]:
        from .model_schema import ModelSchema

        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set.")

        schema = registry.get_model_schema(model)
        if schema and not skip_registry:
            return schema

        model_config_kwargs = {
            "model": model,
            "include": fields,
            "exclude": exclude,
            "skip_registry": skip_registry,
            "depth": depth,
            "registry": registry,
            "optional": optional_fields,
            **model_config_options,
        }
        cls.get_model_config(**model_config_kwargs)  # type: ignore
        new_schema = (
            cls._get_schema_v1(name, model_config_kwargs, ModelSchema)
            if IS_PYDANTIC_V1
            else cls._get_schema_v2(name, model_config_kwargs, ModelSchema)
        )

        new_schema = cast(Type[ModelSchema], new_schema)
        if not skip_registry:
            registry.register_model(model, new_schema)
        return new_schema

    @classmethod
    def _get_schema_v1(
        cls, name: str, model_config_kwargs: typing.Dict, model_type: typing.Type
    ) -> Union[Type["ModelSchema"], Type["Schema"], None]:
        model_config = cls.get_model_config(**model_config_kwargs)

        attrs = {"Config": model_config}

        new_schema = type(name, (model_type,), attrs)
        new_schema = cast(Type["ModelSchema"], new_schema)
        return new_schema

    @classmethod
    def _get_schema_v2(
        cls, name: str, model_config_kwargs: typing.Dict, model_type: typing.Type
    ) -> Union[Type["ModelSchema"], Type["Schema"]]:
        model_config = cls.get_model_config(**model_config_kwargs)
        new_schema_result = {}  # type:ignore[var-annotated]
        new_schema_string = f"""class {name}(model_type):
            class Config(model_config):
                pass """

        exec(new_schema_string, locals(), new_schema_result)
        return new_schema_result.get(name)  # type:ignore[return-value]
