from enum import Enum
from itertools import chain
from typing import Optional, Union, Any, List, no_type_check, Dict, Type

from django.core.paginator import Page
from pydantic.class_validators import extract_root_validators
from pydantic.fields import ModelField, Undefined, FieldInfo
from pydantic.typing import resolve_annotations, get_origin, get_args
from pydantic.utils import ClassAttribute, generate_model_signature, is_valid_field, validate_field_name, \
    lenient_issubclass, ROOT_KEY, unique_list

from .utils.converter import convert_django_field_with_choices
from ninja.schema import DjangoGetter
from pydantic import BaseModel, ConfigError, BaseConfig, PyObject
from pydantic.main import ModelMetaclass, ANNOTATED_FIELD_UNTOUCHED_TYPES, validate_custom_root_type
from django.db import models
from django.db.models import QuerySet
from .factory import SchemaFactory
from .schema_registry import register as global_registry
from ninja_extra.pydanticutils import compute_field_annotations
from .model_validators import ModelValidatorGroup

ALL_FIELDS = '__all__'

__all__ = ['ModelSchema']


namespace_keys = [
    "__config__", "__fields__", "__validators__", "__pre_root_validators__", "__post_root_validators__",
    "__schema_cache__", "__json_encoder__", "__custom_root_type__", "__private_attributes__",
    "__slots__", "__hash__", "__class_vars__", '__annotations__'
]


class PydanticNamespace:
    __annotations__ = dict()
    __config__ = None
    __fields__ = dict()
    __validators__ = ModelValidatorGroup({})
    __pre_root_validators__ = []
    __post_root_validators__ = []
    __custom_root_type__ = None
    __private_attributes__ = None
    __class_vars__ = set()

    def __init__(self, cls):
        for key in namespace_keys:
            value = getattr(cls, key, getattr(self, key, None))
            setattr(self, key, value)


def update_class_missing_fields(cls, bases, namespace):
    old_namespace = PydanticNamespace(cls)
    fields: Dict[str, ModelField] = old_namespace.__fields__ or {}
    config = old_namespace.__config__

    untouched_types = ANNOTATED_FIELD_UNTOUCHED_TYPES

    def is_untouched(v: Any) -> bool:
        return isinstance(v, untouched_types) or v.__class__.__name__ == 'cython_function_or_method'

    vg = ModelValidatorGroup(old_namespace.__validators__)
    new_annotations = resolve_annotations(namespace.get('__annotations__') or {}, getattr(cls, '__module__', None))
    # annotation only fields need to come first in fields
    class_vars = old_namespace.__class_vars__

    for ann_name, ann_type in new_annotations.items():
        if is_valid_field(ann_name):
            validate_field_name(bases, ann_name)
            value = namespace.get(ann_name, Undefined)
            allowed_types = get_args(ann_type) if get_origin(ann_type) is Union else (ann_type,)
            if (
                    is_untouched(value)
                    and ann_type != PyObject
                    and not any(lenient_issubclass(get_origin(allowed_type), Type) for allowed_type in allowed_types)
            ):
                continue
            fields[ann_name] = ModelField.infer(
                name=ann_name,
                value=value,
                annotation=ann_type,
                class_validators=vg.get_validators(ann_name),
                config=config,
            )

    for var_name, value in namespace.items():
        can_be_changed = var_name not in class_vars and not is_untouched(value)
        if is_valid_field(var_name) and var_name not in new_annotations and can_be_changed:
            validate_field_name(bases, var_name)
            inferred = ModelField.infer(
                name=var_name,
                value=value,
                annotation=new_annotations.get(var_name, Undefined),
                class_validators=vg.get_validators(var_name),
                config=config,
            )
            if var_name in fields and inferred.type_ != fields[var_name].type_:
                raise TypeError(
                    f'The type of {cls.__name__}.{var_name} differs from the new default value; '
                    f'if you wish to change the type of this field, please use a type annotation'
                )
            fields[var_name] = inferred

    _custom_root_type = ROOT_KEY in fields
    if _custom_root_type:
        validate_custom_root_type(fields)
    vg.check_for_unused()

    old_namespace.__annotations__.update(new_annotations)
    pre_rv_new, post_rv_new = extract_root_validators(namespace)

    new_namespace = {
        '__annotations__': old_namespace.__annotations__,
        '__config__': config,
        '__fields__': fields,
        '__validators__': vg.validators,
        '__pre_root_validators__': unique_list(old_namespace.__pre_root_validators__ + pre_rv_new),
        '__post_root_validators__': unique_list(old_namespace.__post_root_validators__ + post_rv_new),
        '__class_vars__': class_vars,
    }
    for k, v in new_namespace.items():
        if hasattr(cls, k):
            setattr(cls, k, v)
    # set __signature__ attr only for model class, but not for its instances
    cls.__signature__ = ClassAttribute('__signature__', generate_model_signature(cls.__init__, fields, config))
    return cls


class ModelSchemaBuildActionEnum(Enum):
    READ = 'read'
    CREATE = 'create'


class ModelSchemaConfig(BaseConfig):
    def __init__(self, options=None):
        super(ModelSchemaConfig, self).__init__()
        self.model = getattr(options, 'model', None)
        self.build_schema_action: ModelSchemaBuildActionEnum = ModelSchemaBuildActionEnum[
            getattr(options, 'build_schema_action', 'READ')
        ]
        self.include = getattr(options, 'include', None) or '__all__'
        self.exclude = set(getattr(options, 'exclude', None) or ())
        self.skip_registry = getattr(options, 'skip_registry', False)
        self.registry = getattr(options, 'registry', global_registry)
        self.optional = getattr(options, 'optional', None)
        self.write_only = set(getattr(options, 'write_only', None) or ())
        self.read_only = set(getattr(options, 'read_only', None) or ())
        self.depth = int(getattr(options, 'depth', 0))

    @classmethod
    def clone_field(cls, field: FieldInfo, **kwargs) -> FieldInfo:
        field_dict = dict(field.__repr_args__())
        field_dict.update(**kwargs)
        new_field = FieldInfo(**field_dict)
        return new_field

    def validate_configuration(self):
        self.include = None if self.include == ALL_FIELDS else set(self.include or ())

        action = getattr(self, f"_{self.build_schema_action.value}", None)

        if not self.model:
            raise ConfigError("Invalid Configuration. 'model' is required")

        if not action:
            raise ConfigError("Invalid Configuration. Please choosen between 'read'or 'create'")

        if self.include and self.exclude:
            raise ConfigError("Only one of 'include' or 'exclude' should be set in configuration.")

        if self.write_only.intersection(self.read_only):
            raise ConfigError("'write_only' and 'read_only' should not have any thing in common")

    def process_build_schema_parameters(self):
        self.validate_configuration()
        self.read_only.add(getattr(self.model._meta.pk, 'name', getattr(self.model._meta.pk, 'attname')))
        action = getattr(self, f"_{self.build_schema_action.value}", None)
        action()

    def _read(self):
        self.exclude.update(self.write_only)

    def _create(self):
        self.exclude.update(self.read_only)

    def is_field_in_optional(self, field_name: str) -> bool:
        if not self.optional:
            return False
        if isinstance(self.optional, (set, tuple, list)) and field_name in self.optional:
            return True
        if self.optional == ALL_FIELDS:
            return True
        return False


class ModelSchemaMetaclass(ModelMetaclass):
    @no_type_check
    def __new__(
            mcs, name: str, bases: tuple, namespace: dict,
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases == (BaseModel,) or not namespace.get('Config'):
            return cls

        if issubclass(cls, ModelSchema):
            config = namespace["Config"]
            config_instance = ModelSchemaConfig(config)
            config_instance.process_build_schema_parameters()
            annotations = namespace.get("__annotations__", {})

            try:
                fields = SchemaFactory.model_fields(config_instance.model)
            except AttributeError as exc:
                raise ConfigError(f"{exc} (Is `Config.model` a valid Django model class?)")

            field_values = {}
            _seen = set()

            for field in chain(fields, annotations.copy()):
                field_name = getattr(
                    field, "name", getattr(field, "related_name", field)
                )

                if (
                        field_name in _seen
                        or (config_instance.include and field_name not in config_instance.include)
                        or (config_instance.exclude and field_name in config_instance.exclude)
                ):
                    continue

                _seen.add(field_name)
                if field_name in annotations and field_name in namespace:

                    python_type = annotations.pop(field_name)
                    pydantic_field = namespace[field_name]
                    if (
                            hasattr(pydantic_field, "default_factory")
                            and pydantic_field.default_factory
                    ):
                        pydantic_field = pydantic_field.default_factory()

                elif field_name in annotations:
                    python_type = annotations.pop(field_name)
                    pydantic_field = (
                        None if Optional[python_type] == python_type else Ellipsis
                    )

                else:
                    python_type, pydantic_field = convert_django_field_with_choices(
                        field, registry=config_instance.registry, depth=config_instance.depth,
                        skip_registry=config_instance.skip_registry
                    )
                    if config_instance.is_field_in_optional(field_name):
                        pydantic_field = ModelSchemaConfig.clone_field(field=pydantic_field, default=None)

                field_values[field_name] = (python_type, pydantic_field)

            cls.__doc__ = namespace.get("__doc__", config_instance.model.__doc__)
            cls = update_class_missing_fields(cls, bases, compute_field_annotations(namespace, **field_values))
            return cls
        return cls


class ModelSchema(BaseModel, metaclass=ModelSchemaMetaclass):
    class Config:
        orm_mode = True
        getter_dict = DjangoGetter

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

    @classmethod
    def _get_model_config(cls, **kwargs):
        optional = kwargs.get('optional', getattr(cls.Config, 'optional', None))
        include = kwargs.get('include', getattr(cls.Config, 'include', None))
        exclude = kwargs.get('exclude', getattr(cls.Config, 'exclude', None))
        write_only = kwargs.get('write_only', getattr(cls.Config, 'write_only', None))
        read_only = kwargs.get('read_only', getattr(cls.Config, 'read_only', None))
        action = kwargs.get('action')
        skip_registry = kwargs.get('skip_registry')
        registry = kwargs.get('registry')

        attrs = dict(Config=SchemaFactory.get_model_config(
            optional=optional, include=include, exclude=exclude, write_only=write_only,
            read_only=read_only, action=action, skip_registry=skip_registry, registry=registry
        ))
        return attrs

    @classmethod
    def _build_new_schema(cls, *, name, action, registry, **kwargs):
        skip_registry = kwargs.get('skip_registry', False)
        attrs = cls._get_model_config(
            **kwargs, action=action, skip_registry=skip_registry, registry=registry
        )

        new_schema = type(name, (ModelSchema,), attrs)
        if not skip_registry:
            registry.register_schema(name, new_schema)
        return new_schema

    @classmethod
    def get_create_schema(cls, *, name=None, **kwargs):
        action = kwargs.get('action', 'create')
        name = name or f"{action.capitalize()}{cls.Config.model.name}Schema"

        registry = kwargs.get('registry', getattr(cls.Config, 'registry', global_registry))
        schema = registry.get_schema(name=name)
        if schema:
            return schema

        return cls._build_new_schema(name=name, action=action, registry=registry, **kwargs)

    @classmethod
    def get_update_schema(cls, *, name=None, **kwargs):
        action = kwargs.get('action', 'create')
        name = name or f"{action.capitalize()}{cls.Config.model.name}Schema"

        registry = kwargs.get('registry', getattr(cls.Config, 'registry', global_registry))
        schema = registry.get_schema(name=name)
        if schema:
            return schema

        return cls._build_new_schema(name=name, action=action, registry=registry, **kwargs)

    @classmethod
    def get_patch_schema(cls,  *, name=None, **kwargs):
        action = kwargs.get('action', 'create')
        name = name or f"{action.capitalize()}{cls.Config.model.name}Schema"

        registry = kwargs.get('registry', getattr(cls.Config, 'registry', global_registry))
        schema = registry.get_schema(name=name)
        if schema:
            return schema
        optional = ALL_FIELDS

        kwargs.setdefault('optional', optional)
        return cls._build_new_schema(name=name, action=action, registry=registry, **kwargs)

# create a class APIModelSchema whose purpose to create ModelSchema during API route creation
