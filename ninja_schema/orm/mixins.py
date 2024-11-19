import typing as t

from django.db.models import Model as DjangoModel

from ninja_schema.orm.getters import DjangoGetter
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from ninja_schema.types import DictStrAny

if t.TYPE_CHECKING:
    from pydantic.functional_validators import ModelWrapValidatorHandler

    ModelWrapValidatorHandlerAny = t.TypeVar(
        "ModelWrapValidatorHandlerAny", bound=ModelWrapValidatorHandler[t.Any]
    )


class BaseMixins:
    def apply_to_model(
        self, model_instance: t.Type[DjangoModel], **kwargs: DictStrAny
    ) -> t.Type[DjangoModel]:
        for attr, value in self.dict(**kwargs).items():  # type:ignore[attr-defined]
            setattr(model_instance, attr, value)
        return model_instance


if not IS_PYDANTIC_V1:
    from pydantic import BaseModel, model_validator
    from pydantic.json_schema import GenerateJsonSchema
    from pydantic_core.core_schema import ValidationInfo

    class BaseMixinsV2(BaseMixins):
        model_config: t.Dict[str, t.Any]

        @model_validator(mode="wrap")
        @classmethod
        def _run_root_validator(
            cls,
            values: t.Any,
            handler: "ModelWrapValidatorHandlerAny",
            info: ValidationInfo,
        ) -> t.Any:
            """
            If Pydantic intends to validate against the __dict__ of the immediate Schema
            object, then we need to call `handler` directly on `values` before the conversion
            to DjangoGetter, since any checks or modifications on DjangoGetter's __dict__
            will not persist to the original object.
            """
            forbids_extra = cls.model_config.get("extra") == "forbid"
            should_validate_assignment = cls.model_config.get(
                "validate_assignment", False
            )
            if forbids_extra or should_validate_assignment:
                handler(values)

            values = DjangoGetter(values, cls, info.context)
            return handler(values)

        # @model_validator(mode="before")
        # def _run_root_validator(cls, values: t.Any, info: ValidationInfo) -> t.Any:
        #     values = DjangoGetter(values, cls, info.context)
        #     return values

        @classmethod
        def from_orm(cls, obj: t.Any, **options: t.Any) -> BaseModel:
            return cls.model_validate(  # type:ignore[attr-defined,no-any-return]
                obj, **options
            )

        def dict(self, *a: t.Any, **kw: t.Any) -> DictStrAny:
            # Backward compatibility with pydantic 1.x
            return self.model_dump(*a, **kw)  # type:ignore[attr-defined,no-any-return]

        @classmethod
        def json_schema(cls) -> DictStrAny:
            return cls.model_json_schema(  # type:ignore[attr-defined,no-any-return]
                schema_generator=GenerateJsonSchema
            )

        @classmethod
        def schema(cls) -> DictStrAny:
            return cls.json_schema()

    BaseMixins = BaseMixinsV2  # type:ignore[misc]


class SchemaMixins(BaseMixins):
    pass
