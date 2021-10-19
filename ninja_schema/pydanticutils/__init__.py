import warnings
from typing import TYPE_CHECKING, Any

from pydantic.utils import is_valid_field

from ..errors import ConfigError

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny

__all__ = ["compute_field_annotations"]


def compute_field_annotations(
    namespace: "DictStrAny",
    **field_definitions: Any,
) -> "DictStrAny":

    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if not is_valid_field(f_name):
            warnings.warn(
                f'fields may not start with an underscore, ignoring "{f_name}"',
                RuntimeWarning,
            )
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
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
