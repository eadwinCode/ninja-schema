from typing import TYPE_CHECKING, Dict, Tuple, Type, Union

from django.db.models import Model
from django.db.models.fields import Field as DjangoField
from pydantic.fields import FieldInfo

from .schema import Schema
from .utils.utils import is_valid_class, is_valid_django_model

if TYPE_CHECKING:
    from .model_schema import ModelSchema

__all__ = ["SchemaRegister", "register"]


class SchemaRegisterBorg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class SchemaRegister(SchemaRegisterBorg):
    schemas: Dict[str, Union[Type["ModelSchema"], Type[Schema]]]
    fields: Dict[str, Tuple]

    def __init__(self):
        SchemaRegisterBorg.__init__(self)
        if not hasattr(self, "schemas"):
            self._shared_state.update(schemas={}, fields={})

    def register_model(self, model: Type[Model], schema: Type["ModelSchema"]):
        from .model_schema import ModelSchema

        assert is_valid_class(schema) and issubclass(
            schema, (ModelSchema,)
        ), "Only Schema can be" 'registered, received "{}"'.format(schema.__name__)
        assert is_valid_django_model(
            model
        ), "Only Django Models are allowed. {}".format(model.__name__)
        # TODO: register model as module_name.model_name
        self.register_schema(str(model), schema)

    def register_schema(
        self, name: str, schema: Union[Type["ModelSchema"], Type[Schema]]
    ):
        self.schemas[name] = schema

    def get_converted_field(self, field: DjangoField):
        if str(field) in self.fields:
            return self.fields[str(field)]
        return None

    def register_converted_field(self, field: DjangoField, value: Tuple):
        assert isinstance(
            field, DjangoField
        ), "Only Django Models Fields are allowed. {}".format(field.__name__)
        assert isinstance(value, tuple) and isinstance(
            value[1], FieldInfo
        ), "Value must be a tuple of (type, FieldInfo)"
        self.fields[str(field)] = value

    def get_model_schema(self, model):
        return self.get_schema(model)

    def get_schema(self, name):
        if name in self.schemas:
            return self.schemas[name]
        return None


register = SchemaRegister()
