import json

import pydantic
import pytest

from ninja_schema import ModelSchema, SchemaFactory, model_validator
from ninja_schema.errors import ConfigError
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from tests.models import Event


class TestModelSchema:
    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_schema_include_fields(self):
        class EventSchema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"

        print(EventSchema.schema())
        assert EventSchema.schema() == {
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "category_id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Category",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date"],
            "title": "EventSchema",
            "type": "object",
        }

        class Event2Schema(ModelSchema):
            class Config:
                model = Event
                include = ["title", "start_date", "end_date"]

        print(json.dumps(Event2Schema.schema(), sort_keys=False, indent=4))
        assert Event2Schema.schema() == {
            "properties": {
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date"],
            "title": "Event2Schema",
            "type": "object",
        }

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_schema_depth(self):
        class EventDepthSchema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"
                depth = 1

        print(json.dumps(EventDepthSchema.schema(), sort_keys=False, indent=4))
        assert EventDepthSchema.schema() == {
            "$defs": {
                "Category": {
                    "properties": {
                        "id": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": None,
                            "description": "",
                            "title": "Id",
                        },
                        "name": {
                            "description": "",
                            "maxLength": 100,
                            "title": "Name",
                            "type": "string",
                        },
                        "start_date": {
                            "description": "",
                            "format": "date",
                            "title": "Start Date",
                            "type": "string",
                        },
                        "end_date": {
                            "description": "",
                            "format": "date",
                            "title": "End Date",
                            "type": "string",
                        },
                    },
                    "required": ["name", "start_date", "end_date"],
                    "title": "Category",
                    "type": "object",
                }
            },
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "category": {
                    "anyOf": [{"$ref": "#/$defs/Category"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Category",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date"],
            "title": "EventDepthSchema",
            "type": "object",
        }

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_schema_exclude_fields(self):
        class Event3Schema(ModelSchema):
            class Config:
                model = Event
                exclude = ["id", "category"]

        assert Event3Schema.schema() == {
            "properties": {
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date"],
            "title": "Event3Schema",
            "type": "object",
        }

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_schema_optional_fields(self):
        class Event4Schema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"
                optional = "__all__"

        assert Event4Schema.schema() == {
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "title": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Title",
                },
                "category": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Category",
                },
                "start_date": {
                    "anyOf": [{"format": "date", "type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Start Date",
                },
                "end_date": {
                    "anyOf": [{"format": "date", "type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "End Date",
                },
            },
            "title": "Event4Schema",
            "type": "object",
        }

        class Event5Schema(ModelSchema):
            class Config:
                model = Event
                include = ["id", "title", "start_date"]
                optional = [
                    "start_date",
                ]

        print(Event5Schema.schema())
        assert Event5Schema.schema() == {
            "properties": {
                "id": {"description": "", "title": "Id", "type": "integer"},
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "start_date": {
                    "anyOf": [{"format": "date", "type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Start Date",
                },
            },
            "required": ["id", "title"],
            "title": "Event5Schema",
            "type": "object",
        }

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_schema_custom_fields(self):
        class Event6Schema(ModelSchema):
            custom_field1: str
            custom_field2: int = 1
            custom_field3: str = ""
            __custom_field4 = []  # ignored by pydantic

            class Config:
                model = Event
                exclude = ["id", "category"]

        assert Event6Schema.schema() == {
            "properties": {
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
                "custom_field1": {"title": "Custom Field1", "type": "string"},
                "custom_field2": {
                    "default": 1,
                    "title": "Custom Field2",
                    "type": "integer",
                },
                "custom_field3": {
                    "default": "",
                    "title": "Custom Field3",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date", "custom_field1"],
            "title": "Event6Schema",
            "type": "object",
        }

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_model_validator(self):
        class EventSchema(ModelSchema):
            class Config:
                model = Event
                include = [
                    "title",
                    "start_date",
                ]

            @model_validator("title")
            def validate_title(cls, value):
                return f"{value} - value cleaned"

        event = EventSchema(start_date="2021-06-12", title="PyConf 2021")
        assert "value cleaned" in event.title

        class Event2Schema(ModelSchema):
            custom_field: str

            class Config:
                model = Event
                include = [
                    "title",
                    "start_date",
                ]

            @model_validator("title", "custom_field")
            def validate_title(cls, value):
                return f"{value} - value cleaned"

        event2 = Event2Schema(
            start_date="2021-06-12",
            title="PyConf 2021",
            custom_field="some custom name",
        )
        assert "value cleaned" in event2.title
        assert "value cleaned" in event2.custom_field

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_invalid_fields_inputs(self):
        with pytest.raises(ConfigError):

            class Event1Schema(ModelSchema):
                class Config:
                    model = Event
                    include = ["xy", "yz"]

        with pytest.raises(ConfigError):

            class Event2Schema(ModelSchema):
                class Config:
                    model = Event
                    exclude = ["xy", "yz"]

        with pytest.raises(ConfigError):

            class Event3Schema(ModelSchema):
                class Config:
                    model = Event
                    optional = ["xy", "yz"]

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_model_validator_not_used(self):
        with pytest.raises(pydantic.errors.PydanticUserError):

            class Event1Schema(ModelSchema):
                class Config:
                    model = Event
                    exclude = [
                        "title",
                    ]

                @model_validator("title")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

        with pytest.raises(pydantic.errors.PydanticUserError):

            class Event2Schema(ModelSchema):
                class Config:
                    model = Event
                    include = [
                        "title",
                    ]

                @model_validator("title", "invalid_field")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_factory_functions(self):
        event_schema = SchemaFactory.create_schema(model=Event, name="EventSchema")
        print(json.dumps(event_schema.schema(), sort_keys=False, indent=4))
        assert event_schema.schema() == {
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "title": {
                    "description": "",
                    "maxLength": 100,
                    "title": "Title",
                    "type": "string",
                },
                "category_id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Category",
                },
                "start_date": {
                    "description": "",
                    "format": "date",
                    "title": "Start Date",
                    "type": "string",
                },
                "end_date": {
                    "description": "",
                    "format": "date",
                    "title": "End Date",
                    "type": "string",
                },
            },
            "required": ["title", "start_date", "end_date"],
            "title": "EventSchema",
            "type": "object",
        }

    def get_new_event(self, title):
        event = Event(title=title)
        event.save()
        return event

    @pytest.mark.django_db
    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_getter_functions(self):
        class EventSchema(ModelSchema):
            class Config:
                model = Event
                include = ["title", "category", "id"]

        event = self.get_new_event(title="PyConf")
        json_event = EventSchema.from_orm(event)

        assert json_event.dict() == {"id": 1, "title": "PyConf", "category": None}
        json_event.title = "PyConf Updated"

        json_event.apply_to_model(event)
        assert event.title == "PyConf Updated"

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_abstract_model_schema_does_not_raise_exception_for_incomplete_configuration(
        self,
    ):
        with pytest.raises(
            Exception, match="Invalid Configuration. 'model' is required"
        ):

            class AbstractModel(ModelSchema):
                class Config:
                    orm_mode = True

        class AbstractBaseModelSchema(ModelSchema):
            class Config:
                ninja_schema_abstract = True

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_model_validator_with_new_model_config(self):
        from pydantic import ConfigDict

        class EventWithNewModelConfig(ModelSchema):
            model_config = ConfigDict(
                model=Event,
                include=[
                    "title",
                    "start_date",
                ],
            )

            @model_validator("title")
            def validate_title(cls, value):
                return f"{value} - value cleaned"

        event = EventWithNewModelConfig(start_date="2021-06-12", title="PyConf 2021")
        assert "value cleaned" in event.title
