import inspect
from typing import Type

from django.db import models
from django.db.models import Model


def is_valid_django_model(model: Type[Model]) -> bool:
    return is_valid_class(model) and issubclass(model, models.Model)


def is_valid_class(klass: type) -> bool:
    return inspect.isclass(klass)
