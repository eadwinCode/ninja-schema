import json

import pytest
from pydantic import ValidationError

from ninja_schema import ModelSchema
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from tests.models import Student, StudentEmail


class TestCustomFields:
    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_enum_field(self):
        class StudentSchema(ModelSchema):
            model_config = {"model": Student, "include": "__all__"}

        print(json.dumps(StudentSchema.schema(), sort_keys=False, indent=4))
        assert StudentSchema.schema() == {
            "$defs": {
                "SemesterEnum": {
                    "enum": ["1", "2", "3"],
                    "title": "SemesterEnum",
                    "type": "string",
                }
            },
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "semester": {
                    "allOf": [{"$ref": "#/$defs/SemesterEnum"}],
                    "default": "1",
                    "description": "",
                    "title": "Semester",
                },
            },
            "title": "StudentSchema",
            "type": "object",
        }
        schema_instance = StudentSchema(semester="1")
        assert str(schema_instance.json()) == '{"id":null,"semester":"1"}'
        with pytest.raises(ValidationError):
            StudentSchema(semester="something")

    @pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
    def test_email_field(self):
        class StudentEmailSchema(ModelSchema):
            class Config:
                model = StudentEmail
                include = "__all__"

        print(json.dumps(StudentEmailSchema.schema(), sort_keys=False, indent=4))
        assert StudentEmailSchema.schema() == {
            "properties": {
                "id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
                "email": {
                    "description": "",
                    "format": "email",
                    "title": "Email",
                    "type": "string",
                },
            },
            "required": ["email"],
            "title": "StudentEmailSchema",
            "type": "object",
        }
        assert (
            str(StudentEmailSchema(email="email@example.com").json())
            == '{"id":null,"email":"email@example.com"}'
        )
        with pytest.raises(ValidationError):
            StudentEmailSchema(email="emailexample.com")
