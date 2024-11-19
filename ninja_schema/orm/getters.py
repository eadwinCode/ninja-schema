import typing as t

import pydantic
from django.db.models import Manager, QuerySet
from django.db.models.fields.files import FieldFile

from ninja_schema.pydanticutils import IS_PYDANTIC_V1

__all__ = [
    "DjangoGetter",
]


class DjangoGetterMixin:
    def _convert_result(self, result: t.Any) -> t.Any:
        if isinstance(result, Manager):
            return list(result.all())

        elif isinstance(result, getattr(QuerySet, "__origin__", QuerySet)):
            return list(result)

        elif isinstance(result, FieldFile):
            if not result:
                return None
            return result.url

        return result


if IS_PYDANTIC_V1:
    from pydantic.utils import GetterDict

    pydantic_version = list(map(int, pydantic.VERSION.split(".")))[:2]
    assert pydantic_version >= [1, 6], "Pydantic 1.6+ required"

    class DjangoGetter(GetterDict, DjangoGetterMixin):
        def get(self, key: t.Any, default: t.Any = None) -> t.Any:
            result = super().get(key, default)
            return self._convert_result(result)

else:

    class DjangoGetter(DjangoGetterMixin):  # type:ignore[no-redef]
        __slots__ = ("_obj", "_schema_cls", "_context")

        def __init__(self, obj: t.Any, schema_cls: t.Any, context: t.Any = None):
            self._obj = obj
            self._schema_cls = schema_cls
            self._context = context

        def __getattr__(self, key: str) -> t.Any:
            # if key.startswith("__pydantic"):
            #     return getattr(self._obj, key)
            if isinstance(self._obj, dict):
                if key not in self._obj:
                    raise AttributeError(key)
                value = self._obj[key]
            else:
                try:
                    value = getattr(self._obj, key)
                except AttributeError as e:
                    raise AttributeError(key) from e

            return self._convert_result(value)
