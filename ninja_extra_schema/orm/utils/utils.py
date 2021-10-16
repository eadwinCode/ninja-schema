import inspect
from typing import Type, Optional, Any

from django.db import models
from django.db.models import Model


def is_valid_django_model(model: Type[Model]) -> bool:
    return inspect.isclass(model) and issubclass(model, models.Model)


def import_single_dispatch() -> Optional[Any]:
    try:
        from functools import singledispatch
    except ImportError:
        singledispatch = None

    if not singledispatch:
        try:
            from singledispatch import singledispatch
        except ImportError:
            pass

    if not singledispatch:
        raise Exception(
            "It seems your python version does not include "
            "functools.singledispatch. Please install the 'singledispatch' "
            "package. More information here: "
            "https://pypi.python.org/pypi/singledispatch"
        )

    return singledispatch
