from typing import Dict, Tuple, Type
from django.db.models import Model
from django.db.models.fields import Field as DjangoField
from pydantic.fields import FieldInfo

from .schema import Schema

__all__ = ["SchemaRegister", "register"]


class SchemaRegisterBorg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class SchemaRegister(SchemaRegisterBorg):
    types: Dict[str, Dict[str, Type[Schema]]]

    def __init__(self):
        SchemaRegisterBorg.__init__(self)
        if not hasattr(self, 'schemas'):
            # TODO: register Django UserModel
            self._shared_state.update(types=dict(schemas={}, fields={}))

    def register_model(self, model: Model, schema: Type[Schema]):
        from .model_schema import ModelSchema
        assert issubclass(schema, (ModelSchema,)), (
            "Only Schema can be"
            'registered, received "{}"'.format(schema.__name__)
        )
        assert issubclass(model, (Model,)), (
            "Only Django Models are allowed. {}".format(model.__name__)
        )
        # TODO: register model as module_name.model_name
        self.register_schema(model, schema)

    def register_schema(self, name: str, schema: Type[Schema]):
        self.types['schemas'][name] = schema

    def get_converted_field(self, field: DjangoField):
        if field in self.types['fields']:
            return self.types['fields'][field]
        return None

    def register_converted_field(self, field: DjangoField, value: Tuple):
        assert isinstance(field, DjangoField), (
            "Only Django Models Fields are allowed. {}".format(field.__name__)
        )
        assert isinstance(value, tuple) and isinstance(value[1], FieldInfo), (
            "Value must be a tuple of (type, FieldInfo)"
        )
        self.types['fields'][field] = value

    def get_model_schema(self, model):
        return self.get_schema(model)

    def get_schema(self, name):
        if name in self.types['schemas']:
            return self.types['schemas'][name]
        return None


register = SchemaRegister()
