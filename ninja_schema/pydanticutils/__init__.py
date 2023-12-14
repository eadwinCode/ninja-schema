import logging
import warnings
from typing import TYPE_CHECKING, Any

from pydantic.version import VERSION as _PYDANTIC_VERSION

from ..errors import ConfigError

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny

__all__ = ["compute_field_annotations", "IS_PYDANTIC_V1", "PYDANTIC_VERSION"]

logger = logging.getLogger()

PYDANTIC_VERSION = list(map(int, _PYDANTIC_VERSION.split(".")))[:2]
IS_PYDANTIC_V1 = PYDANTIC_VERSION[0] == 1


def is_valid_field_name(name: str) -> bool:
    return not name.startswith("_")


def compute_field_annotations(
    namespace: "DictStrAny",
    **field_definitions: Any,
) -> "DictStrAny":
    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if not is_valid_field_name(f_name):  # pragma: no cover
            warnings.warn(
                f'fields may not start with an underscore, ignoring "{f_name}"',
                RuntimeWarning,
                stacklevel=1,
            )
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:  # pragma: no cover
                raise ConfigError(
                    "field definitions should either be a tuple of (<type>, <default>) or just a "
                    "default value, unfortunately this means tuples as "
                    "default values are not allowed"
                ) from e
        else:
            f_annotation, f_value = None, f_def

        if f_annotation:
            annotations[f_name] = f_annotation
        fields[f_name] = f_value

    namespace.update(**{"__annotations__": annotations})
    namespace.update(fields)

    return namespace
