from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union, cast
from django.db.models import Field, ManyToManyRel, ManyToOneRel, Model
from pydantic import create_model as create_pydantic_model

from ninja.errors import ConfigError
from ninja_extra_scheme.orm.fields import get_schema_field, get_related_field_schema, construct_fields
from ninja_extra_scheme.orm.schema import Schema
from pydantic.fields import FieldInfo

__all__ = ["SchemaFactory", "factory", "create_schema"]
SchemaKey = Tuple[Type[Model], str, int, str, str, str]


class ModelSchema(dict):
    # 'get', 'post', 'update', 'patch'
    fields: Optional[List[str]] = None
    exclude: Optional[List[str]] = None

    def __init__(self, model: Model, fields=None, exclude=None, **kwargs):
        super(ModelSchema, self).__init__(**kwargs)
        self.model = model
        self.pk_name = model._meta.pk.name
        self.fields = fields
        self.exclude = exclude
        self.model_fields = dict()
        self.related_fields = dict()
        self.related_field_ids = dict()

    def _selected_model_fields(
            self,
            model_fields: Dict[str, Tuple],
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            extra_fields: List[str] = None,
            extra_exclude: List[str] = None
    ) -> Iterator[Tuple]:
        """Returns iterator for model fields based on `exclude` or `fields` arguments"""
        _fields = fields or self.fields
        _excludes = exclude or self.exclude

        if not _fields and not _excludes:
            for field_name, value in model_fields.items():
                if extra_exclude and field_name in extra_exclude:
                    continue
                yield field_name, value

        if _fields:
            _field_combined = set(_fields).union(set(extra_fields or [])) - set(extra_exclude or [])
            for name in _field_combined:
                yield name, model_fields[name]

        if _excludes:
            _exclude_combined = set(_excludes).union(set(extra_exclude or [])) - set(extra_fields or [])
            for field_name, value in model_fields.items():
                if field_name not in _exclude_combined:
                    yield field_name, value

    def get_fields(
            self,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ):
        definitions = {}
        models = self.model_fields.copy()
        models.update(**self.related_fields)
        for field_name, value in self._selected_model_fields(
                extra_fields=[self.pk_name], fields=fields, exclude=exclude, model_fields=models
        ):
            definitions[field_name] = value
        return definitions

    def post_fields(
            self,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ):
        definitions = {}
        models = self.model_fields.copy()
        models.update(**self.related_field_ids)
        for field_name, value in self._selected_model_fields(
                extra_exclude=[self.pk_name], fields=fields, exclude=exclude, model_fields=models):
            definitions[field_name] = value
        return definitions

    def update_fields(
            self,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ):
        definitions = {}
        models = self.model_fields.copy()
        models.update(**self.related_field_ids)
        for field_name, value in self._selected_model_fields(
                extra_exclude=[self.pk_name], fields=fields, exclude=exclude, model_fields=models):
            definitions[field_name] = value
        return definitions

    def patch_fields(
            self,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ):
        definitions = {}
        models = self.model_fields.copy()
        models.update(**self.related_field_ids)
        for field_name, (python_type, field) in self._selected_model_fields(
                extra_exclude=[self.pk_name], fields=fields, exclude=exclude, model_fields=models
        ):
            new_field = self.clone_field(field=field, default=None)
            definitions[field_name] = python_type, new_field
        return definitions

    @classmethod
    def clone_field(cls, field: FieldInfo, **kwargs) -> FieldInfo:
        field_dict = dict(field.__repr_args__())
        field_dict.update(**kwargs)
        new_field = FieldInfo(**field_dict)
        return new_field

    def create_schema_for_action(
            self,
            *,
            action: str,
            name: str = "",
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            custom_fields: Optional[List[Tuple[str, str, Any]]] = None,
    ):

        name = name or f"{action.capitalize()}{str(self.model.__name__).capitalize()}Schema"
        action_method = getattr(self, f"{action.lower()}_fields", None)
        if not action_method:
            raise Exception("Schema action is invalid. Choose read, create, update, patch")

        definitions = action_method(fields=fields, exclude=exclude)
        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                definitions[fld_name] = (python_type, field_info)

        schema = cast(
            Type[Schema],
            create_pydantic_model(name, __base__=Schema, **definitions),  # type: ignore
        )
        self[action] = schema
        return schema


class SchemaFactory:
    def __init__(self) -> None:
        self.schemas: Dict[Model, ModelSchema] = {}

    def create_schema(
            self,
            model: Type[Model],
            *,
            action: str = "get",  # 'get', 'create', 'update', 'patch'
            name: str = "",
            depth: int = 0,
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
            custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
    ) -> Type[Schema]:

        if fields and exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set.")

        key = model
        if key in self.schemas:
            model_schema = self.schemas[key]
            if action in model_schema:
                return model_schema[action]
            return model_schema.create_schema_for_action(
                action=action, fields=fields, exclude=exclude,
                custom_fields=custom_fields, name=name
            )

        model_schema = ModelSchema(model=model, fields=fields, exclude=exclude)
        depth = depth or 2
        for fld in self._all_model_fields(model):
            python_type, field_info = get_schema_field(fld, depth=depth)
            if fld.is_relation:
                model_schema.related_field_ids[fld.name] = (python_type, field_info)
                if depth > 0:
                    python_type, field_info = get_related_field_schema(fld, depth=depth)
                    model_schema.related_fields[fld.name] = (python_type, field_info)
                continue
            model_schema.model_fields[fld.name] = (python_type, field_info)

        schema = model_schema.create_schema_for_action(
            action=action, fields=fields, exclude=exclude,
            custom_fields=custom_fields, name=name
        )
        self.schemas[model] = model_schema
        return schema

    def _all_model_fields(
            self,
            model: Type[Model],
            fields: Optional[List[str]] = None,
            exclude: Optional[List[str]] = None,
    ) -> Iterator[Field]:
        """Returns iterator for model fields based on `exclude` or `fields` arguments"""
        all_fields_ = construct_fields(model, fields=fields, exclude=exclude)
        all_fields = {f.name: f for f in self._model_fields(model)}
        invalid_fields = (set(fields or []) | set(exclude or [])) - all_fields.keys()
        if invalid_fields:
            raise ConfigError(f"Field(s) {invalid_fields} are not in model.")

        for f in all_fields.values():
            yield f

    @classmethod
    def _model_fields(cls, model: Type[Model]) -> Iterator[Field]:
        """returns iterator with all the fields that can be part of schema"""
        for fld in model._meta.get_fields():
            if isinstance(fld, (ManyToOneRel, ManyToManyRel)):
                # skipping relations
                continue
            yield cast(Field, fld)


factory = SchemaFactory()
create_schema = factory.create_schema

