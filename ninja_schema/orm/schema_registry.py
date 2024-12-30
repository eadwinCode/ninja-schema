from typing import TYPE_CHECKING, Dict, Tuple, Type, Union

from django.db.models import Model

from .schema import Schema
from .utils.utils import is_valid_class, is_valid_django_model

if TYPE_CHECKING:
    from ninja_schema.orm.model_schema import ModelSchema

__all__ = ["SchemaRegister", "registry"]


class SchemaRegisterBorg:
    _shared_state: Dict[str, Dict] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


class SchemaRegister(SchemaRegisterBorg):
    schemas: Dict[Type[Model], Union[Type["ModelSchema"], Type[Schema]]]
    fields: Dict[str, Tuple]

    def __init__(self) -> None:
        SchemaRegisterBorg.__init__(self)
        if not hasattr(self, "schemas"):
            self._shared_state.update(schemas={}, fields={})

    def register_model(self, model: Type[Model], schema: Type["ModelSchema"]) -> None:
        from ninja_schema.orm.model_schema import ModelSchema

        assert is_valid_class(schema) and issubclass(schema, (ModelSchema,)), (
            "Only Schema can be" 'registered, received "{}"'.format(schema.__name__)
        )
        assert is_valid_django_model(
            model
        ), "Only Django Models are allowed. {}".format(model.__name__)
        # TODO: register model as module_name.model_name
        self.register_schema(model, schema)

    def register_schema(
        self, name: Type[Model], schema: Union[Type["ModelSchema"], Type[Schema]]
    ) -> None:
        self.schemas[name] = schema

    def get_model_schema(
        self, model: Type[Model]
    ) -> Union[Type["ModelSchema"], Type[Schema], None]:
        if model in self.schemas:
            return self.schemas[model]
        return None


registry = SchemaRegister()
