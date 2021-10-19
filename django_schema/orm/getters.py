from typing import Any

import pydantic
from django.db.models import Manager, QuerySet
from django.db.models.fields.files import FieldFile
from pydantic.utils import GetterDict

pydantic_version = list(map(int, pydantic.VERSION.split(".")))[:2]
assert pydantic_version >= [1, 6], "Pydantic 1.6+ required"

__all__ = [
    "DjangoGetter",
]


class DjangoGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        result = super().get(key, default)

        if isinstance(result, Manager):
            return list(result.all())

        elif isinstance(result, getattr(QuerySet, "__origin__", QuerySet)):
            return list(result)

        elif isinstance(result, FieldFile):
            if not result:
                return None
            return result.url

        return result
