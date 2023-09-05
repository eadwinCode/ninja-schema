import json
from unittest.mock import Mock

import django
import pytest
from django.db import models
from django.db.models import Manager
from pydantic import ValidationError

from ninja_schema import ModelSchema
from ninja_schema.pydanticutils import IS_PYDANTIC_V1
from tests.models import Week


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_inheritance():
    class ParentModel(models.Model):
        parent_field = models.CharField()

        class Meta:
            app_label = "tests"

    class ChildModel(ParentModel):
        child_field = models.CharField()

        class Meta:
            app_label = "tests"

    class ChildSchema(ModelSchema):
        class Config:
            model = ChildModel

    print(ChildSchema.schema())

    assert ChildSchema.schema() == {
        "properties": {
            "id": {"description": "", "title": "Id", "type": "integer"},
            "parent_field": {
                "description": "",
                "title": "Parent Field",
                "type": "string",
            },
            "parentmodel_ptr": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Parentmodel Ptr",
            },
            "child_field": {
                "description": "",
                "title": "Child Field",
                "type": "string",
            },
        },
        "required": ["id", "parent_field", "child_field"],
        "title": "ChildSchema",
        "type": "object",
    }


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_all_fields():
    # test all except relational field

    class AllFields(models.Model):
        bigintegerfield = models.BigIntegerField()
        binaryfield = models.BinaryField()
        booleanfield = models.BooleanField()
        charfield = models.CharField()
        commaseparatedintegerfield = models.CommaSeparatedIntegerField()
        datefield = models.DateField()
        datetimefield = models.DateTimeField()
        decimalfield = models.DecimalField()
        durationfield = models.DurationField()
        emailfield = models.EmailField()
        filefield = models.FileField()
        filepathfield = models.FilePathField()
        floatfield = models.FloatField()
        genericipaddressfield = models.GenericIPAddressField()
        ipaddressfield = models.IPAddressField()
        imagefield = models.ImageField()
        integerfield = models.IntegerField()
        nullbooleanfield = models.NullBooleanField()
        positiveintegerfield = models.PositiveIntegerField()
        positivesmallintegerfield = models.PositiveSmallIntegerField()
        slugfield = models.SlugField()
        smallintegerfield = models.SmallIntegerField()
        textfield = models.TextField()
        timefield = models.TimeField()
        urlfield = models.URLField()
        uuidfield = models.UUIDField()

        class Meta:
            app_label = "tests"

    class AllFieldsSchema(ModelSchema):
        class Config:
            model = AllFields

    # print(SchemaCls.schema())
    assert AllFieldsSchema.schema() == {
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Id",
            },
            "bigintegerfield": {
                "description": "",
                "title": "Bigintegerfield",
                "type": "integer",
            },
            "binaryfield": {
                "description": "",
                "format": "binary",
                "title": "Binaryfield",
                "type": "string",
            },
            "booleanfield": {
                "description": "",
                "title": "Booleanfield",
                "type": "boolean",
            },
            "charfield": {"description": "", "title": "Charfield", "type": "string"},
            "commaseparatedintegerfield": {
                "description": "",
                "title": "Commaseparatedintegerfield",
                "type": "string",
            },
            "datefield": {
                "description": "",
                "format": "date",
                "title": "Datefield",
                "type": "string",
            },
            "datetimefield": {
                "description": "",
                "format": "date-time",
                "title": "Datetimefield",
                "type": "string",
            },
            "decimalfield": {
                "anyOf": [{"type": "number"}, {"type": "string"}],
                "description": "",
                "title": "Decimalfield",
            },
            "durationfield": {
                "description": "",
                "format": "duration",
                "title": "Durationfield",
                "type": "string",
            },
            "emailfield": {
                "description": "",
                "format": "email",
                "title": "Emailfield",
                "type": "string",
            },
            "filefield": {"description": "", "title": "Filefield", "type": "string"},
            "filepathfield": {
                "description": "",
                "title": "Filepathfield",
                "type": "string",
            },
            "floatfield": {"description": "", "title": "Floatfield", "type": "number"},
            "genericipaddressfield": {
                "description": "",
                "format": "ipvanyaddress",
                "title": "Genericipaddressfield",
                "type": "string",
            },
            "ipaddressfield": {
                "description": "",
                "format": "ipvanyaddress",
                "title": "Ipaddressfield",
                "type": "string",
            },
            "imagefield": {"description": "", "title": "Imagefield", "type": "string"},
            "integerfield": {
                "description": "",
                "title": "Integerfield",
                "type": "integer",
            },
            "nullbooleanfield": {
                "description": "",
                "title": "Nullbooleanfield",
                "type": "boolean",
            },
            "positiveintegerfield": {
                "description": "",
                "title": "Positiveintegerfield",
                "type": "integer",
            },
            "positivesmallintegerfield": {
                "description": "",
                "title": "Positivesmallintegerfield",
                "type": "integer",
            },
            "slugfield": {"description": "", "title": "Slugfield", "type": "string"},
            "smallintegerfield": {
                "description": "",
                "title": "Smallintegerfield",
                "type": "integer",
            },
            "textfield": {"description": "", "title": "Textfield", "type": "string"},
            "timefield": {
                "description": "",
                "format": "time",
                "title": "Timefield",
                "type": "string",
            },
            "urlfield": {
                "description": "",
                "format": "uri",
                "minLength": 1,
                "title": "Urlfield",
                "type": "string",
            },
            "uuidfield": {
                "description": "",
                "format": "uuid",
                "title": "Uuidfield",
                "type": "string",
            },
        },
        "required": [
            "bigintegerfield",
            "binaryfield",
            "booleanfield",
            "charfield",
            "commaseparatedintegerfield",
            "datefield",
            "datetimefield",
            "decimalfield",
            "durationfield",
            "emailfield",
            "filefield",
            "filepathfield",
            "floatfield",
            "genericipaddressfield",
            "ipaddressfield",
            "imagefield",
            "integerfield",
            "nullbooleanfield",
            "positiveintegerfield",
            "positivesmallintegerfield",
            "slugfield",
            "smallintegerfield",
            "textfield",
            "timefield",
            "urlfield",
            "uuidfield",
        ],
        "title": "AllFieldsSchema",
        "type": "object",
    }


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_bigautofield():
    # primary key are optional fields when include = __all__
    class ModelBigAuto(models.Model):
        bigautofiled = models.BigAutoField(primary_key=True)

        class Meta:
            app_label = "tests"

    class ModelBigAutoSchema(ModelSchema):
        class Config:
            model = ModelBigAuto

    print(ModelBigAutoSchema.schema())
    assert ModelBigAutoSchema.schema() == {
        "properties": {
            "bigautofiled": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Bigautofiled",
            }
        },
        "title": "ModelBigAutoSchema",
        "type": "object",
    }


@pytest.mark.skipif(
    django.VERSION < (3, 1), reason="json field introduced in django 3.1"
)
@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_django_31_fields():
    class ModelNewFields(models.Model):
        jsonfield = models.JSONField()
        positivebigintegerfield = models.PositiveBigIntegerField()

        class Meta:
            app_label = "tests"

    class ModelNewFieldsSchema(ModelSchema):
        class Config:
            model = ModelNewFields

    print(ModelNewFieldsSchema.schema())
    assert ModelNewFieldsSchema.schema() == {
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Id",
            },
            "jsonfield": {
                "contentMediaType": "application/json",
                "contentSchema": {},
                "description": "",
                "title": "Jsonfield",
                "type": "string",
            },
            "positivebigintegerfield": {
                "description": "",
                "title": "Positivebigintegerfield",
                "type": "integer",
            },
        },
        "required": ["jsonfield", "positivebigintegerfield"],
        "title": "ModelNewFieldsSchema",
        "type": "object",
    }

    with pytest.raises(ValidationError):
        ModelNewFieldsSchema(id=1, jsonfield={"any": "data"}, positivebigintegerfield=1)

    obj = ModelNewFieldsSchema(
        id=1, jsonfield=json.dumps({"any": "data"}), positivebigintegerfield=1
    )
    assert obj.dict() == {
        "id": 1,
        "jsonfield": {"any": "data"},
        "positivebigintegerfield": 1,
    }


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_relational():
    class Related(models.Model):
        charfield = models.CharField()

        class Meta:
            app_label = "tests"

    class TestModel(models.Model):
        manytomanyfield = models.ManyToManyField(Related)
        onetoonefield = models.OneToOneField(Related, on_delete=models.CASCADE)
        foreignkey = models.ForeignKey(Related, on_delete=models.SET_NULL, null=True)

        class Meta:
            app_label = "tests"

    class TestSchema(ModelSchema):
        class Config:
            model = TestModel

    print(json.dumps(TestSchema.schema(), sort_keys=False, indent=4))
    assert TestSchema.schema() == {
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Id",
            },
            "onetoonefield_id": {
                "description": "",
                "title": "Onetoonefield",
                "type": "integer",
            },
            "foreignkey_id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Foreignkey",
            },
            "manytomanyfield": {
                "description": "",
                "items": {"type": "integer"},
                "title": "Manytomanyfield",
                "type": "array",
            },
        },
        "required": ["onetoonefield_id", "manytomanyfield"],
        "title": "TestSchema",
        "type": "object",
    }


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_default():
    class MyModel(models.Model):
        default_static = models.CharField(default="hello")
        default_dynamic = models.CharField(default=lambda: "world")

        class Meta:
            app_label = "tests"

    class MyModelSchema(ModelSchema):
        class Config:
            model = MyModel

    print(json.dumps(MyModelSchema.schema(), sort_keys=False, indent=4))
    assert MyModelSchema.schema() == {
        "properties": {
            "id": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "default": None,
                "description": "",
                "title": "Id",
            },
            "default_static": {
                "default": "hello",
                "description": "",
                "title": "Default Static",
                "type": "string",
            },
            "default_dynamic": {
                "description": "",
                "title": "Default Dynamic",
                "type": "string",
            },
        },
        "title": "MyModelSchema",
        "type": "object",
    }


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_manytomany():
    class Foo(models.Model):
        f = models.CharField()

        class Meta:
            app_label = "tests"

    class Bar(models.Model):
        m2m = models.ManyToManyField(Foo, blank=True)

        class Meta:
            app_label = "tests"

    class BarSchema(ModelSchema):
        class Config:
            model = Bar

    # mocking database data:

    foo = Mock()
    foo.pk = 1
    foo.f = "test"

    m2m = Mock(spec=Manager)
    m2m.all = lambda: [foo]

    bar = Mock()
    bar.id = 1
    bar.m2m = m2m

    data = BarSchema.from_orm(bar).dict()

    assert data == {"id": 1, "m2m": [1]}


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="requires pydantic == 2.1.x")
def test_manytomany_validation():
    bar = Mock()
    bar.pk = "555555s"

    foo = Mock()
    foo.pk = 1

    class WeekSchema(ModelSchema):
        class Config:
            model = Week

    with pytest.raises(Exception, match="Invalid type"):
        WeekSchema(name="FirstWeek", days=["1", "2"])

    with pytest.raises(Exception, match="Invalid type"):
        WeekSchema(name="FirstWeek", days=[bar, bar])

    schema = WeekSchema(name="FirstWeek", days=[foo, foo])
    assert schema.dict() == {"id": None, "name": "FirstWeek", "days": [1, 1]}
