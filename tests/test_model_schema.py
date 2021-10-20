import json

import pytest

from ninja_schema import ModelSchema, SchemaFactory, model_validator
from ninja_schema.errors import ConfigError
from tests.models import Event


class TestModelSchema:
    def test_schema_include_fields(self):
        class EventSchema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"

        assert EventSchema.schema() == {
            "title": "EventSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category_id": {"title": "Category", "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

        class Event2Schema(ModelSchema):
            class Config:
                model = Event
                include = ["title", "start_date", "end_date"]

        assert Event2Schema.schema() == {
            "title": "Event2Schema",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    def test_schema_depth(self):
        class EventDepthSchema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"
                depth = 1

        assert EventDepthSchema.schema() == {
            "title": "EventDepthSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category": {
                    "title": "Category",
                    "allOf": [{"$ref": "#/definitions/Category"}],
                },
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
            "definitions": {
                "Category": {
                    "title": "Category",
                    "type": "object",
                    "properties": {
                        "id": {"title": "Id", "extra": {}, "type": "integer"},
                        "name": {"title": "Name", "maxLength": 100, "type": "string"},
                        "start_date": {
                            "title": "Start Date",
                            "type": "string",
                            "format": "date",
                        },
                        "end_date": {
                            "title": "End Date",
                            "type": "string",
                            "format": "date",
                        },
                    },
                    "required": ["name", "start_date", "end_date"],
                }
            },
        }

    def test_schema_exclude_fields(self):
        class Event3Schema(ModelSchema):
            class Config:
                model = Event
                exclude = ["id", "category"]

        assert Event3Schema.schema() == {
            "title": "Event3Schema",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    def test_schema_optional_fields(self):
        class Event4Schema(ModelSchema):
            class Config:
                model = Event
                include = "__all__"
                optional = "__all__"

        assert Event4Schema.schema() == {
            "title": "Event4Schema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {
                    "title": "Title",
                    "extra": {},
                    "maxLength": 100,
                    "type": "string",
                },
                "category_id": {"title": "Category", "extra": {}, "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
                "end_date": {
                    "title": "End Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
            },
        }

        class Event5Schema(ModelSchema):
            class Config:
                model = Event
                include = ["id", "title", "start_date"]
                optional = [
                    "start_date",
                ]

        assert Event5Schema.schema() == {
            "title": "Event5Schema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "extra": {},
                    "type": "string",
                    "format": "date",
                },
            },
            "required": [
                "id",
                "title",
            ],
        }

    def test_schema_custom_fields(self):
        class Event6Schema(ModelSchema):
            custom_field1: str
            custom_field2: int = 1
            custom_field3 = ""
            _custom_field4 = []  # ignored by pydantic

            class Config:
                model = Event
                exclude = ["id", "category"]

        assert Event6Schema.schema() == {
            "title": "Event6Schema",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
                "custom_field1": {"title": "Custom Field1", "type": "string"},
                "custom_field3": {
                    "title": "Custom Field3",
                    "default": "",
                    "type": "string",
                },
                "custom_field2": {
                    "title": "Custom Field2",
                    "default": 1,
                    "type": "integer",
                },
            },
            "required": ["custom_field1", "title", "start_date", "end_date"],
        }

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

    def test_model_validator_not_used(self):
        with pytest.raises(ConfigError):

            class Event1Schema(ModelSchema):
                class Config:
                    model = Event
                    exclude = [
                        "title",
                    ]

                @model_validator("title")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

        with pytest.raises(ConfigError):

            class Event2Schema(ModelSchema):
                class Config:
                    model = Event
                    include = [
                        "title",
                    ]

                @model_validator("title", "invalid_field")
                def validate_title(cls, value):
                    return f"{value} - value cleaned"

    def test_factory_functions(self):
        event_schema = SchemaFactory.create_schema(model=Event, name="EventSchema")
        print(json.dumps(event_schema.schema(), sort_keys=False, indent=4))
        assert event_schema.schema() == {
            "title": "EventSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "title": {"title": "Title", "maxLength": 100, "type": "string"},
                "category_id": {"title": "Category", "type": "integer"},
                "start_date": {
                    "title": "Start Date",
                    "type": "string",
                    "format": "date",
                },
                "end_date": {"title": "End Date", "type": "string", "format": "date"},
            },
            "required": ["title", "start_date", "end_date"],
        }

    def get_new_event(self, title):
        event = Event(title=title)
        event.save()
        return event

    @pytest.mark.django_db
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
