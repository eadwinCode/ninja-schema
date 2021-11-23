import json
from unittest.mock import Mock

import django
import pytest
from django.db import models
from django.db.models import Manager

from ninja_schema import ModelSchema


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
        "title": "ChildSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer"},
            "parent_field": {"title": "Parent Field", "type": "string"},
            "parentmodel_ptr_id": {
                "title": "Parentmodel Ptr",
                "type": "integer",
                "extra": {},
            },
            "child_field": {"title": "Child Field", "type": "string"},
        },
        "required": ["id", "parent_field", "child_field"],
    }


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
        "title": "AllFieldsSchema",
        "type": "object",
        "properties": {
            "id": {"extra": {}, "title": "Id", "type": "integer"},
            "bigintegerfield": {"title": "Bigintegerfield", "type": "integer"},
            "binaryfield": {
                "title": "Binaryfield",
                "type": "string",
                "format": "binary",
            },
            "booleanfield": {"title": "Booleanfield", "type": "boolean"},
            "charfield": {"title": "Charfield", "type": "string"},
            "commaseparatedintegerfield": {
                "title": "Commaseparatedintegerfield",
                "type": "string",
            },
            "datefield": {"title": "Datefield", "type": "string", "format": "date"},
            "datetimefield": {
                "title": "Datetimefield",
                "type": "string",
                "format": "date-time",
            },
            "decimalfield": {"title": "Decimalfield", "type": "number"},
            "durationfield": {
                "title": "Durationfield",
                "type": "number",
                "format": "time-delta",
            },
            "emailfield": {"title": "Emailfield", "format": "email", "type": "string"},
            "filefield": {"title": "Filefield", "type": "string"},
            "filepathfield": {"title": "Filepathfield", "type": "string"},
            "floatfield": {"title": "Floatfield", "type": "number"},
            "genericipaddressfield": {
                "title": "Genericipaddressfield",
                "type": "string",
                "format": "ipvanyaddress",
            },
            "ipaddressfield": {
                "title": "Ipaddressfield",
                "type": "string",
                "format": "ipvanyaddress",
            },
            "imagefield": {"title": "Imagefield", "type": "string"},
            "integerfield": {"title": "Integerfield", "type": "integer"},
            "nullbooleanfield": {"title": "Nullbooleanfield", "type": "boolean"},
            "positiveintegerfield": {
                "title": "Positiveintegerfield",
                "type": "integer",
            },
            "positivesmallintegerfield": {
                "title": "Positivesmallintegerfield",
                "type": "integer",
            },
            "slugfield": {"title": "Slugfield", "type": "string"},
            "smallintegerfield": {"title": "Smallintegerfield", "type": "integer"},
            "textfield": {"title": "Textfield", "type": "string"},
            "timefield": {"title": "Timefield", "type": "string", "format": "time"},
            "urlfield": {
                "title": "Urlfield",
                "type": "string",
                "format": "uri",
                "maxLength": 65536,
                "minLength": 1,
            },
            "uuidfield": {"title": "Uuidfield", "type": "string", "format": "uuid"},
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
    }


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
        "title": "ModelBigAutoSchema",
        "type": "object",
        "properties": {
            "bigautofiled": {"title": "Bigautofiled", "type": "integer", "extra": {}}
        },
    }


@pytest.mark.skipif(
    django.VERSION < (3, 1), reason="json field introduced in django 3.1"
)
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
        "title": "ModelNewFieldsSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "type": "integer", "extra": {}},
            "jsonfield": {
                "title": "Jsonfield",
                "format": "json-string",
                "type": "string",
            },
            "positivebigintegerfield": {
                "title": "Positivebigintegerfield",
                "type": "integer",
            },
        },
        "required": ["jsonfield", "positivebigintegerfield"],
    }
    with pytest.raises(Exception):
        ModelNewFieldsSchema(id=1, jsonfield={"any": "data"}, positivebigintegerfield=1)

    obj = ModelNewFieldsSchema(
        id=1, jsonfield=json.dumps({"any": "data"}), positivebigintegerfield=1
    )
    assert obj.dict() == {
        "id": 1,
        "jsonfield": {"any": "data"},
        "positivebigintegerfield": 1,
    }


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

    print(TestSchema.schema())
    assert TestSchema.schema() == {
        "title": "TestSchema",
        "type": "object",
        "properties": {
            "id": {"extra": {}, "title": "Id", "type": "integer"},
            "onetoonefield_id": {"title": "Onetoonefield", "type": "integer"},
            "foreignkey_id": {"title": "Foreignkey", "type": "integer"},
            "manytomanyfield": {
                "title": "Manytomanyfield",
                "type": "array",
                "items": {"type": "integer"},
            },
        },
        "required": ["onetoonefield_id", "manytomanyfield"],
    }


def test_default():
    class MyModel(models.Model):
        default_static = models.CharField(default="hello")
        default_dynamic = models.CharField(default=lambda: "world")

        class Meta:
            app_label = "tests"

    class MyModelSchema(ModelSchema):
        class Config:
            model = MyModel

    assert MyModelSchema.schema() == {
        "title": "MyModelSchema",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "extra": {}, "type": "integer"},
            "default_static": {
                "title": "Default Static",
                "default": "hello",
                "type": "string",
            },
            "default_dynamic": {"title": "Default Dynamic", "type": "string"},
        },
    }


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
