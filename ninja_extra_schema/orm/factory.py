from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union, cast

from django.db.models import Field, ManyToManyRel, ManyToOneRel, Model
from pydantic import create_model as create_pydantic_model, BaseConfig
from ninja_extra_scheme.pydanticutils import compute_field_annotations
from ninja.errors import ConfigError
from ninja.orm.fields import get_schema_field
from .schema import Schema
from .schema_registry import SchemaRegister
from .utils.converter import convert_django_field_with_choices

__all__ = ["SchemaFactory", ]


class SchemaFactory:
    # @classmethod
    # def create_schema(
    #         cls,
    #         model: Type[Model],
    #         *,
    #         registry: SchemaRegister,
    #         name: str = "",
    #         depth: int = 0,
    #         fields: Optional[List[str]] = None,
    #         exclude: Optional[List[str]] = None,
    #         custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
    #         skip_register=False
    # ) -> Type[Schema]:
    #     name = name or model.__name__
    #
    #     if fields and exclude:
    #         raise ConfigError("Only one of 'include' or 'exclude' should be set.")
    #
    #     schema = registry.get_model_schema(model)
    #     if schema:
    #         return schema
    #
    #     definitions = cls.get_model_fields_definitions(
    #         model=model, fields=fields, exclude=exclude, depth=depth
    #     )
    #     if custom_fields:
    #         for fld_name, python_type, field_info in custom_fields:
    #             definitions[fld_name] = (python_type, field_info)
    #
    #     schema = cls.create_schema_from_definitions(
    #         model, name=name, definitions=definitions,
    #         skip_register=skip_register, registry=registry
    #     )
    #     return schema
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
            custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
            skip_registry=False
    ) -> Type[Schema]:
        from .model_schema import ModelSchema
        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set.")

        schema = registry.get_model_schema(model)
        if schema:
            return schema

        ModelConfig = cls.get_model_config(
            model=model, include=fields, exclude=exclude, skip_registry=skip_registry,
            depth=depth, registry=registry,
        )

        custom_fields_definitions = {}
        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                custom_fields_definitions[fld_name] = (python_type, field_info)

        namespace = compute_field_annotations({}, **custom_fields_definitions)
        attrs = dict(Config=ModelConfig)
        attrs.update(namespace)

        new_schema = type(name, (ModelSchema,), attrs)

        if not skip_registry:
            registry.register_model(model, new_schema)
        return new_schema

    @classmethod
    def get_model_fields_definitions(cls, *, model, fields, exclude, depth=0):
        definitions = {}
        for fld in cls._selected_model_fields(model, fields, exclude):
            python_type, field_info = get_schema_field(fld, depth=depth)
            definitions[fld.name] = (python_type, field_info)
        return definitions

    @classmethod
    def _selected_model_fields(
            cls,
            model: Type[Model],
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ) -> Iterator[Field]:
        """Returns iterator for model fields based on `exclude` or `fields` arguments"""
        all_fields = {f.name: f for f in cls.model_fields(model)}

        if not fields and not exclude:
            for f in all_fields.values():
                yield f

        invalid_fields = (set(fields or []) | set(exclude or [])) - all_fields.keys()
        if invalid_fields:
            raise ConfigError(f"Field(s) {invalid_fields} are not in model.")

        if fields:
            for name in fields:
                yield all_fields[name]
        if exclude:
            for f in all_fields.values():
                if f.name not in exclude:
                    yield f

    @classmethod
    def model_fields(cls, model: Type[Model]) -> Iterator[Field]:
        """returns iterator with all the fields that can be part of schema"""
        for fld in model._meta.get_fields():
            if isinstance(fld, (ManyToOneRel, ManyToManyRel)):
                # skipping relations
                continue
            yield cast(Field, fld)

    @classmethod
    def get_model_fields_schema(cls, model: Type[Model], *, registry: SchemaRegister) -> Iterator[Field]:
        """returns iterator with all the fields that can be part of schema"""
        fields = {}
        for field in cls.model_fields(model):
            convert_django_field_with_choices(field, registry=registry)

    @classmethod
    def create_schema_from_definitions(
            cls, model: Model, *, name: str, definitions: Dict[Any, Any],
            skip_register: bool, registry: SchemaRegister, base=Schema
    ):
        schema = cast(
            Type[Schema],
            create_pydantic_model(name, __base__=base, **definitions),  # type: ignore
        )
        if not skip_register:
            registry.register_model(model, schema)
        return schema
