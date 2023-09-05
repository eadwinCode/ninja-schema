import json

import pytest
from pydantic import ValidationError

from ninja_schema import ModelSchema
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from tests.models import Student, StudentEmail


class TestCustomFields:
    @pytest.mark.skipif(not IS_PYDANTIC_V1, reason="requires pydantic == 1.6.x")
    def test_enum_field(self):
        class StudentSchema(ModelSchema):
            class Config:
                model = Student
                include = "__all__"

        print(json.dumps(StudentSchema.schema(), sort_keys=False, indent=4))
        assert StudentSchema.schema() == {
            "title": "StudentSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "semester": {
                    "title": "Semester",
                    "default": "1",
                    "allOf": [{"$ref": "#/definitions/SemesterEnum"}],
                },
            },
            "definitions": {
                "SemesterEnum": {
                    "title": "SemesterEnum",
                    "description": "An enumeration.",
                    "enum": ["1", "2", "3"],
                }
            },
        }
        schema_instance = StudentSchema(semester="1")
        assert str(schema_instance.json()) == '{"id": null, "semester": "1"}'
        with pytest.raises(ValidationError):
            StudentSchema(semester="something")

    @pytest.mark.skipif(not IS_PYDANTIC_V1, reason="requires pydantic == 1.6.x")
    def test_email_field(self):
        class StudentEmailSchema(ModelSchema):
            class Config:
                model = StudentEmail
                include = "__all__"

        print(json.dumps(StudentEmailSchema.schema(), sort_keys=False, indent=4))
        assert StudentEmailSchema.schema() == {
            "title": "StudentEmailSchema",
            "type": "object",
            "properties": {
                "id": {"title": "Id", "extra": {}, "type": "integer"},
                "email": {"title": "Email", "type": "string", "format": "email"},
            },
            "required": ["email"],
        }
        assert (
            str(StudentEmailSchema(email="email@example.com").json())
            == '{"id": null, "email": "email@example.com"}'
        )
        with pytest.raises(ValidationError):
            StudentEmailSchema(email="emailexample.com")
