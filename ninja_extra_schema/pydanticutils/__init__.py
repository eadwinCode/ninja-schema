import warnings
from typing import Type, Any, Dict, cast, TypeVar, TYPE_CHECKING

from pydantic import BaseConfig, ConfigError
from pydantic.main import BaseModel, inherit_config

from pydantic.utils import is_valid_field

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny
    from pydantic.main import Model

__all__ = ['create_model', 'compute_field_annotations']


def create_model(
    __model_name: str,
    *,
    __config__: Type[BaseConfig] = None,
    __bases__: Type["Model"] = None,
    __module__: str = __name__,
    __validators__: Dict[str, classmethod] = None,
    **field_definitions: Any,
) -> Type["Model"]:
    """
    Dynamically create a model.
    :param __model_name: name of the created model
    :param __config__: config class to use for the new model
    :param __bases__: base class for the new model to inherit from
    :param __module__: module of the created model
    :param __validators__: a dict of method names and @validator class methods
    :param field_definitions: fields of the model (or extra fields if a base is supplied)
        in the format `<name>=(<type>, <default default>)` or `<name>=<default value>, e.g.
        `foobar=(str, ...)` or `foobar=123`, or, for complex use-cases, in the format
        `<name>=<FieldInfo>`, e.g. `foo=Field(default_factory=datetime.utcnow, alias='bar')`
    """

    if __bases__ is not None:
        if __config__ is not None:
            raise ConfigError('to avoid confusion __config__ and __base__ cannot be used together')
    else:
        __bases__ = cast(Type["Model"], BaseModel)

    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if not is_valid_field(f_name):
            warnings.warn(f'fields may not start with an underscore, ignoring "{f_name}"', RuntimeWarning)
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
                raise ConfigError(
                    'field definitions should either be a tuple of (<type>, <default>) or just a '
                    'default value, unfortunately this means tuples as '
                    'default values are not allowed'
                ) from e
        else:
            f_annotation, f_value = None, f_def

        if f_annotation:
            annotations[f_name] = f_annotation
        fields[f_name] = f_value

    namespace: "DictStrAny" = {'__annotations__': annotations, '__module__': __module__}
    if __validators__:
        namespace.update(__validators__)
    namespace.update(fields)
    if __config__:
        namespace['Config'] = inherit_config(__config__, BaseConfig)

    base = __bases__
    if not isinstance(__bases__, (tuple, list)):
        base = (__bases__, )

    return type(__model_name, base, namespace)


def compute_field_annotations(
    namespace:  "DictStrAny", **field_definitions: Any,
) -> "DictStrAny":

    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if not is_valid_field(f_name):
            warnings.warn(f'fields may not start with an underscore, ignoring "{f_name}"', RuntimeWarning)
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
                raise ConfigError(
                    'field definitions should either be a tuple of (<type>, <default>) or just a '
                    'default value, unfortunately this means tuples as '
                    'default values are not allowed'
                ) from e
        else:
            f_annotation, f_value = None, f_def

        if f_annotation:
            annotations[f_name] = f_annotation
        fields[f_name] = f_value

    namespace.update(**{'__annotations__': annotations})
    namespace.update(fields)

    return namespace
