import warnings
from itertools import chain
from types import FunctionType
from typing import Callable, Any
from pydantic.utils import in_ipython
from pydantic import ConfigError
from pydantic.class_validators import VALIDATOR_CONFIG_KEY, Validator, ValidatorGroup
from pydantic.typing import AnyCallable

__all__ = ['model_validator', 'ModelValidatorGroup']


class ModelValidator:
    _FUNCS = set()

    @classmethod
    def _prepare_validator(cls, function: AnyCallable, allow_reuse: bool) -> classmethod:
        """
        Avoid validators with duplicated names since without this, validators can be overwritten silently
        which generally isn't the intended behaviour, don't run in ipython (see #312) or if allow_reuse is False.
        """
        f_cls = function if isinstance(function, classmethod) else classmethod(function)
        if not in_ipython() and not allow_reuse:
            ref = f_cls.__func__.__module__ + '.' + f_cls.__func__.__qualname__
            if ref in cls._FUNCS:
                raise ConfigError(f'duplicate validator function "{ref}"; if this is intended, set `allow_reuse=True`')
            cls._FUNCS.add(ref)
        return f_cls

    @classmethod
    def model_validator(
            cls,
            *fields: str,
            pre: bool = False,
            each_item: bool = False,
            always: bool = False,
            check_fields: bool = False,
            whole: bool = None,
            allow_reuse: bool = True,
    ) -> Callable[[AnyCallable], classmethod]:
        """
        Decorate methods on the class indicating that they should be used to validate fields
        :param fields: which field(s) the method should be called on
        :param pre: whether or not this validator should be called before the standard validators (else after)
        :param each_item: for complex objects (sets, lists etc.) whether to validate individual elements rather than the
          whole object
        :param always: whether this method and other validators should be called even if the value is missing
        :param check_fields: whether to check that the fields actually exist on the model
        :param allow_reuse: whether to track and raise an error if another validator refers to the decorated function
        """
        if not fields:
            raise ConfigError('validator with no fields specified')
        elif isinstance(fields[0], FunctionType):
            raise ConfigError(
                "validators should be used with fields and keyword arguments, not bare. "  # noqa: Q000
                "E.g. usage should be `@validator('<field_name>', ...)`"
            )

        if whole is not None:
            warnings.warn(
                'The "whole" keyword argument is deprecated, use "each_item" (inverse meaning, default False) instead',
                DeprecationWarning,
            )
            assert each_item is False, '"each_item" and "whole" conflict, remove "whole"'
            each_item = not whole

        def dec(f: Any) -> classmethod:
            f_cls = cls._prepare_validator(f, allow_reuse)
            setattr(
                f_cls,
                VALIDATOR_CONFIG_KEY,
                (
                    fields,
                    Validator(func=f_cls.__func__, pre=pre, each_item=each_item, always=always,
                              check_fields=check_fields),
                ),
            )
            return f_cls

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
            fn = ', '.join(unused_validators)
            raise ConfigError(
                f"Validators defined with incorrect fields: {fn} "  # noqa: Q000
                f"(use check_fields=False if you're inheriting from the model and intended this)"
            )
