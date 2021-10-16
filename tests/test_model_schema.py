from ninja_extra_schema import ModelSchema, model_validator
from tests.models import Category, Client, Event


class TestModelSchema:
    def test_schema_include_fields(self):
        class EventSchema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"
                optional = ["category"]

            @model_validator("title")
            def title_validator(cls, value):
                return value

        print(EventSchema.schema())
        scs = EventSchema(
            title="some title", start_date="2021-12-4", end_date="2021-12-4"
        )
        assert str(EventSchema)
