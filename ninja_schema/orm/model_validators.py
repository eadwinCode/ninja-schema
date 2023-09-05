import warnings
from itertools import chain
from types import FunctionType
from typing import Any, Callable, Optional

from ..errors import ConfigError
from ..pydanticutils import IS_PYDANTIC_V1

__all__ = ["model_validator", "ModelValidatorGroup"]

if IS_PYDANTIC_V1:
    from pydantic.class_validators import (
        VALIDATOR_CONFIG_KEY,
        Validator,
        ValidatorGroup,
        _prepare_validator,
    )

    class ModelValidator:
        @classmethod
        def model_validator(
            cls,
            *fields: str,
            pre: bool = False,
            each_item: bool = False,
            always: bool = False,
            check_fields: bool = False,
        ) -> Callable[[Callable], classmethod]:
            """
            Decorate methods on the class indicating that they should be used to validate fields
            :param fields: which field(s) the method should be called on
            :param pre: whether or not this validator should be called before the standard validators (else after)
            :param each_item: for complex objects (sets, lists etc.) whether to validate individual elements rather than the
              whole object
            :param always: whether this method and other validators should be called even if the value is missing
            :param check_fields: whether to check that the fields actually exist on the model
            """
            if not fields:
                raise ConfigError("validator with no fields specified")
            elif isinstance(fields[0], FunctionType):
                raise ConfigError(
                    "validators should be used with fields and keyword arguments, not bare. "  # noqa: Q000
                    "E.g. usage should be `@validator('<field_name>', ...)`"
                )

            def dec(f: Any) -> classmethod:
                f_cls = _prepare_validator(f, True)
                setattr(
                    f_cls,
                    VALIDATOR_CONFIG_KEY,
                    (
                        fields,
                        Validator(
                            func=f_cls.__func__,
                            pre=pre,
                            each_item=each_item,
                            always=always,
                            check_fields=check_fields,
                        ),
                    ),
                )
                return f_cls  # type:ignore[no-any-return]

            return dec

    model_validator = ModelValidator.model_validator

    class ModelValidatorGroup(ValidatorGroup):
        def check_for_unused(self) -> None:
            unused_validators = set(
                chain.from_iterable(
                    (v.func.__name__ for v in self.validators[f])
                    for f in (self.validators.keys() - self.used_validators)
                )
            )
            if unused_validators:
                fn = ", ".join(unused_validators)
                raise ConfigError(
                    f"Validators defined with incorrect fields: {fn} "  # noqa: Q000
                    f"(use check_fields=False if you're inheriting from the model and intended this)"
                )

else:
    from pydantic import field_validator
    from pydantic.functional_validators import FieldValidatorModes

    def model_validator(  # type:ignore[misc]
        __field: str,
        *fields: str,
        mode: FieldValidatorModes = "after",
        check_fields: Optional[bool] = None,
    ) -> Callable[[Any], Any]:
        warnings.warn(
            f"'{model_validator}' is deprecated for pydantic version 2.x.x. "
            f"Use 'field_validator' for the pydantic package instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        return field_validator(__field, *fields, mode=mode, check_fields=check_fields)

    class ModelValidatorGroup:  # type:ignore[no-redef]
        pass
