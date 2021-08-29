# import datetime
# from collections import OrderedDict
# from decimal import Decimal
# from typing import (
#     Any,
#     Callable,
#     Dict,
#     Generator,
#     List,
#     Tuple,
#     Type,
#     TypeVar,
#     no_type_check,
# )
# from uuid import UUID
# from .utils.utils import get_model_fields
# from django.db.models import ManyToManyField, Model, ManyToOneRel, ManyToManyRel
# from django.db.models.fields import Field
# from pydantic import IPvAnyAddress
# from pydantic.fields import FieldInfo, Undefined
# from .utils.converter import convert_django_field_with_choices
# from ninja.openapi.schema import OpenAPISchema
#
# __all__ = ["create_m2m_link_type", "get_schema_field", "get_related_field_schema", "construct_fields"]
#
#
# class AnyObject:
#     @classmethod
#     def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
#         field_schema.update(type="object")
#
#     @classmethod
#     def __get_validators__(cls) -> Generator[Callable, None, None]:
#         yield cls.validate
#
#     @classmethod
#     def validate(cls, value: Any) -> Any:
#         return value
#
#
# TYPES = {
#     "AutoField": int,
#     "BigAutoField": int,
#     "BigIntegerField": int,
#     "BinaryField": bytes,
#     "BooleanField": bool,
#     "CharField": str,
#     "DateField": datetime.date,
#     "DateTimeField": datetime.datetime,
#     "DecimalField": Decimal,
#     "DurationField": datetime.timedelta,
#     "FileField": str,
#     "FilePathField": str,
#     "FloatField": float,
#     "GenericIPAddressField": IPvAnyAddress,
#     "IPAddressField": IPvAnyAddress,
#     "IntegerField": int,
#     "JSONField": AnyObject,
#     "NullBooleanField": bool,
#     "PositiveBigIntegerField": int,
#     "PositiveIntegerField": int,
#     "PositiveSmallIntegerField": int,
#     "SlugField": str,
#     "SmallIntegerField": int,
#     "TextField": str,
#     "TimeField": datetime.time,
#     "UUIDField": UUID,
# }
#
# TModel = TypeVar("TModel")
#
#
# @no_type_check
# def create_m2m_link_type(type_: Type[TModel]) -> Type[TModel]:
#     class M2MLink(type_):  # type: ignore
#         @classmethod
#         def __get_validators__(cls):
#             yield cls.validate
#
#         @classmethod
#         def validate(cls, v):
#             return v.pk
#
#     return M2MLink
#
#
# @no_type_check
# def get_schema_field(field: Field, *, depth: int = 0) -> Tuple:
#     alias = None
#     default = ...
#     default_factory = None
#     max_length = None
#
#     if field.is_relation:
#         internal_type = field.related_model._meta.pk.get_internal_type()
#
#         if not field.concrete and field.auto_created or field.null:
#             default = None
#
#         if hasattr(field, "get_attname"):
#             alias = field.get_attname()
#
#         pk_type = TYPES.get(internal_type, int)
#         if field.one_to_many or field.many_to_many:
#             m2m_type = create_m2m_link_type(pk_type)
#             python_type = List[m2m_type]  # type: ignore
#         else:
#             python_type = pk_type
#
#     else:
#         field_options = field.deconstruct()[3]  # 3 are the keywords
#         blank = field_options.get("blank", False)
#         null = field_options.get("null", False)
#         max_length = field_options.get("max_length")
#
#         internal_type = field.get_internal_type()
#         python_type = TYPES[internal_type]
#
#         if field.has_default():
#             if callable(field.default):
#                 default_factory = field.default
#             else:
#                 default = field.default
#         elif field.primary_key or blank or null:
#             default = None
#
#     if default_factory:
#         default = Undefined
#
#     description = field.help_text
#     title = field.verbose_name.title()
#
#     return (
#         python_type,
#         FieldInfo(
#             default=default,
#             alias=alias,
#             default_factory=default_factory,
#             title=title,
#             description=description,
#             max_length=max_length,
#         ),
#     )
#
#
# @no_type_check
# def get_related_field_schema(field: Field, *, depth: int) -> Tuple[OpenAPISchema, FieldInfo]:
#     from ninja_extra.orm import SchemaFactory
#
#     model = field.related_model
#     schema = SchemaFactory.create_schema(model, depth=depth - 1)
#     default = ...
#     if not field.concrete and field.auto_created or field.null:
#         default = None
#     if isinstance(field, ManyToManyField):
#         schema = List[schema]  # type: ignore
#
#     return (
#         schema,
#         FieldInfo(
#             default=default,
#             description=field.help_text,
#             title=field.verbose_name.title(),
#         ),
#     )
#
#
# def construct_fields(
#         model: Type[Model], *, fields, exclude, convert_choices_to_enum=False, registry=None
# ):
#     _model_fields = get_model_fields(model)
#     _fields = fields or []
#     _exclude = exclude or []
#
#     django_fields = OrderedDict()
#     for name, field in _model_fields:
#         if isinstance(field, (ManyToOneRel, ManyToManyRel)):
#             # skipping relations
#             continue
#
#         _convert_choices_to_enum = convert_choices_to_enum
#         if not isinstance(_convert_choices_to_enum, bool):
#             # then `convert_choices_to_enum` is a list of field names to convert
#             if name in _convert_choices_to_enum:
#                 _convert_choices_to_enum = True
#             else:
#                 _convert_choices_to_enum = False
#
#         converted = convert_django_field_with_choices(
#             field, registry, convert_choices_to_enum=_convert_choices_to_enum
#         )
#         django_fields[name] = converted
#
#     return django_fields
