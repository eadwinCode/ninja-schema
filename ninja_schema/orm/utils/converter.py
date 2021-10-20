import datetime
import re
from enum import Enum
from functools import singledispatch
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    no_type_check,
)
from uuid import UUID

from django.db import models
from django.db.models.fields import Field
from django.utils.encoding import force_str
from pydantic import AnyUrl, EmailStr, Json
from pydantic.fields import FieldInfo, Undefined

from ...compat import ArrayField, HStoreField, JSONField, RangeField
from ...types import DictStrAny
from ..factory import SchemaFactory
from ..schema_registry import SchemaRegister, registry as global_registry

if TYPE_CHECKING:
    from ..model_schema import ModelSchema


TModel = TypeVar("TModel")

NAME_PATTERN = r"^[_a-zA-Z][_a-zA-Z0-9]*$"
COMPILED_NAME_PATTERN = re.compile(NAME_PATTERN)


def assert_valid_name(name: str) -> None:
    """Helper to assert that provided names are valid."""
    assert COMPILED_NAME_PATTERN.match(
        name
    ), 'Names must match /{}/ but "{}" does not.'.format(NAME_PATTERN, name)


def convert_choice_name(name: str) -> str:
    name = force_str(name)
    try:
        assert_valid_name(name)
    except AssertionError:
        name = "A_%s" % name
    return name


def get_choices(
    choices: Iterable[Union[Tuple[Any, Any], Tuple[str, Iterable[Tuple[Any, Any]]]]]
) -> Iterator[Tuple[str, str, str]]:
    for value, help_text in choices:
        if isinstance(help_text, (tuple, list)):
            for choice in get_choices(help_text):
                yield choice
        else:
            name = convert_choice_name(value)
            description = force_str(help_text)
            yield name, value, description


class FieldConversionProps:
    description: str
    blank: bool
    is_null: bool
    max_length: int
    alias: str
    title: str

    def __init__(self, field: Field):
        data = {}
        field_options = field.deconstruct()[3]  # 3 are the keywords

        data["description"] = force_str(
            getattr(field, "help_text", field.verbose_name)
        ).strip()
        data["title"] = field.verbose_name.title()

        if not field.is_relation:
            data["blank"] = field_options.get("blank", False)
            data["is_null"] = field_options.get("null", False)
            data["max_length"] = field_options.get("max_length")
            data.update(alias=None)

        if field.is_relation and hasattr(field, "get_attname"):
            data["alias"] = field.get_attname()

        self.__dict__ = data


def convert_django_field_with_choices(
    field: Field,
    *,
    registry: SchemaRegister,
    depth: int = 0,
    skip_registry: bool = False,
) -> Tuple[Type, FieldInfo]:
    converted = convert_django_field(
        field, registry=registry, depth=depth, skip_registry=skip_registry
    )
    return converted


@singledispatch
def convert_django_field(field: Field, **kwargs: Any) -> Tuple[Type, FieldInfo]:
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" % (field, field.__class__)
    )


@no_type_check
def create_m2m_link_type(type_: Type[TModel]) -> Type[TModel]:
    class M2MLink(type_):  # type: ignore
        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            return v.pk

    return M2MLink


@no_type_check
def construct_related_field_schema(
    field: Field, *, registry: SchemaRegister, depth: int, skip_registry=False
) -> Tuple[Type["ModelSchema"], FieldInfo]:
    # create a sample config and return the type
    model = field.related_model
    schema = SchemaFactory.create_schema(
        model, depth=depth - 1, registry=registry, skip_registry=skip_registry
    )
    default = ...
    if not field.concrete and field.auto_created or field.null:
        default = None
    if isinstance(field, models.ManyToManyField):
        schema = List[schema]  # type: ignore

    return (
        schema,
        FieldInfo(
            default=default,
            description=force_str(
                getattr(field, "help_text", field.verbose_name)
            ).strip(),
            title=field.verbose_name.title(),
        ),
    )


@no_type_check
def construct_relational_field_info(
    field: Field,
    *,
    registry: SchemaRegister,
    depth: int = 0,
    __module__: str = __name__,
) -> Tuple[Type, FieldInfo]:
    default: Any = ...
    field_props = FieldConversionProps(field)

    inner_type, field_info = convert_django_field(
        field.related_model._meta.pk, registry=registry, depth=depth
    )

    if not field.concrete and field.auto_created or field.null:
        default = None

    python_type = inner_type
    if field.one_to_many or field.many_to_many:
        m2m_type = create_m2m_link_type(inner_type)
        python_type = List[m2m_type]  # type: ignore

    field_info = FieldInfo(
        default=default,
        alias=field_props.alias,
        default_factory=None,
        title=field_props.title,
        description=field_props.description,
        max_length=None,
    )
    return python_type, field_info


@no_type_check
def construct_field_info(
    python_type: type,
    field: Field,
    depth: int = 0,
    __module__: str = __name__,
    is_custom_type: bool = False,
) -> Tuple[Type, FieldInfo]:
    default = ...
    default_factory = None

    field_props = FieldConversionProps(field)

    if field.choices:
        choices = list(get_choices(field.choices))
        named_choices = [(c[2], c[1]) for c in choices]
        python_type = Enum(  # type: ignore
            f"{field.name.title().replace('_', '')}Enum",
            named_choices,
            module=__module__,
        )
        is_custom_type = True

    if field.has_default():
        if callable(field.default):
            default_factory = field.default
        elif isinstance(field.default, Enum):
            default = field.default.value
        else:
            default = field.default
    elif field_props.blank or field_props.is_null:
        default = None

    if default_factory:
        default = Undefined

    return (
        python_type,
        FieldInfo(
            default=default,
            alias=field_props.alias,
            default_factory=default_factory,
            title=field_props.title,
            description=field_props.description,
            max_length=None if is_custom_type else field_props.max_length,
        ),
    )


@no_type_check
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.GenericIPAddressField)
@convert_django_field.register(models.FileField)
@convert_django_field.register(models.FilePathField)
def convert_field_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(str, field)


@no_type_check
@convert_django_field.register(models.EmailField)
def convert_field_to_email_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(EmailStr, field, is_custom_type=True)


@no_type_check
@convert_django_field.register(models.URLField)
def convert_field_to_url_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(AnyUrl, field, is_custom_type=True)


@no_type_check
@convert_django_field.register(models.AutoField)
def convert_field_to_id(field: Field, **kwargs: DictStrAny) -> Tuple[Type, FieldInfo]:
    return construct_field_info(int, field)


@no_type_check
@convert_django_field.register(models.UUIDField)
def convert_field_to_uuid(field: Field, **kwargs: DictStrAny) -> Tuple[Type, FieldInfo]:
    return construct_field_info(UUID, field)


@no_type_check
@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def convert_field_to_int(field: Field, **kwargs: DictStrAny) -> Tuple[Type, FieldInfo]:
    return construct_field_info(int, field)


@no_type_check
@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(bool, field)


@no_type_check
@convert_django_field.register(models.NullBooleanField)
def convert_field_to_null_boolean(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(bool, field)


@no_type_check
@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
@convert_django_field.register(models.DurationField)
def convert_field_to_float(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(float, field)


@no_type_check
@convert_django_field.register(models.DateTimeField)
def convert_datetime_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.datetime, field)


@no_type_check
@convert_django_field.register(models.DateField)
def convert_date_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.date, field)


@no_type_check
@convert_django_field.register(models.TimeField)
def convert_time_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_field_info(datetime.time, field)


@no_type_check
@convert_django_field.register(models.OneToOneRel)
def convert_one_to_one_field_to_django_model(
    field: Field, registry=None, depth=0, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    return construct_relational_field_info(field, registry=registry, depth=depth)


@no_type_check
@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(
    field: Field, registry=None, depth=0, skip_registry=False, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    if depth > 0:
        return construct_related_field_schema(
            field, depth=depth, registry=registry, skip_registry=skip_registry
        )
    return construct_relational_field_info(field, registry=registry, depth=depth)


@no_type_check
@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_django_model(
    field: Field,
    registry: Optional[SchemaRegister] = None,
    depth: int = 0,
    skip_registry: bool = False,
    **kwargs: DictStrAny,
) -> Tuple[Type, FieldInfo]:
    if depth > 0:
        return construct_related_field_schema(
            field,
            depth=depth,
            registry=registry or global_registry,
            skip_registry=skip_registry,
        )
    return construct_relational_field_info(field, registry=registry, depth=depth)


@no_type_check
@convert_django_field.register(ArrayField)
def convert_postgres_array_to_list(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    inner_type, field_info = convert_django_field(field.base_field)
    if not isinstance(inner_type, list):
        inner_type = List[inner_type]  # type: ignore
    return inner_type, field_info


@no_type_check
@convert_django_field.register(HStoreField)
@convert_django_field.register(JSONField)
def convert_postgres_field_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    python_type = Json
    if field.null:
        python_type = Optional[Json]
    return construct_field_info(python_type, field)


@no_type_check
@convert_django_field.register(RangeField)
def convert_postgres_range_to_string(
    field: Field, **kwargs: DictStrAny
) -> Tuple[Type, FieldInfo]:
    inner_type, field_info = convert_django_field(field.base_field)
    if not isinstance(inner_type, list):
        inner_type = List[inner_type]  # type: ignore
    return inner_type, field_info
