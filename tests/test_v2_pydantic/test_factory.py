import pytest

from ninja_schema.orm.factory import SchemaFactory
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from tests.models import Event


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_create_schema_with_model_config_options():
    schema = SchemaFactory.create_schema(
        Event,
        skip_registry=True,
        from_attributes=True,  # model_config_option
        title="Custom Title",  # model_config_option
    )

    assert schema.model_config["from_attributes"] is True
    assert schema.model_config["title"] == "Custom Title"
