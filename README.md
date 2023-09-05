![Test](https://github.com/eadwinCode/ninja-schema/workflows/Test/badge.svg)
[![PyPI version](https://badge.fury.io/py/ninja-schema.svg)](https://badge.fury.io/py/ninja-schema)
[![PyPI version](https://img.shields.io/pypi/pyversions/ninja-schema.svg)](https://pypi.python.org/pypi/ninja-schema)
[![PyPI version](https://img.shields.io/pypi/djversions/ninja-schema.svg)](https://pypi.python.org/pypi/ninja-schema)
[![Codecov](https://img.shields.io/codecov/c/gh/eadwinCode/ninja-schema)](https://codecov.io/gh/eadwinCode/ninja-schema)
[![Downloads](https://static.pepy.tech/badge/ninja-schema)](https://pepy.tech/project/ninja-schema)

# Ninja Schema
Ninja Schema converts your Django ORM models to Pydantic schemas with more Pydantic features supported.

**Inspired by**: [django-ninja](https://django-ninja.rest-framework.com/) and [djantic](https://jordaneremieff.github.io/djantic/)
### Notice
Starting version `0.13.4`, Ninja schema will support both v1 and v2 of pydantic library and will closely monitor V1 support on pydantic package.

### Requirements
Python >= 3.8
django >= 3
pydantic >= 1.6

**Key features:**
- **Custom Field Support**: Ninja Schema converts django model to native pydantic types which gives you quick field validation out of the box. eg Enums, email, IPAddress, URLs, JSON, etc
- **Field Validator**: Fields can be validated with **model_validator** just like pydantic **[validator](https://pydantic-docs.helpmanual.io/usage/validators/)** or **[root_validator](https://pydantic-docs.helpmanual.io/usage/validators/)**. 
  
## Installation

```
pip install ninja-schema
```

## Example
Checkout this sample project: https://github.com/eadwinCode/bookstoreapi


## Configuration Properties
- **model**: Django Model
- **include**: Fields to include, `default: '__all__'`. Please note that when include = `__all__`, model's **PK** becomes optional
- **exclude**: Fields to exclude, `default: set()`
- **optional**: Fields to mark optional,` default: set()`
`optional = '__all__'` will make all schema fields optional 
- **depth**: defines depth to nested generated schema, `default: 0`

## `model_validator(*args, **kwargs)`
**model_validator** is a substitute for **pydantic [validator](https://pydantic-docs.helpmanual.io/usage/validators/)** used for pre and post fields validation.
There functionalities are the same. More info [pydantic validators](https://pydantic-docs.helpmanual.io/usage/validators/)
```Python
from django.contrib.auth import get_user_model
from ninja_schema import ModelSchema, model_validator

UserModel = get_user_model()


class CreateUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ['username', 'email', 'password']

    @model_validator('username')
    def validate_unique_username(cls, value_data: str) -> str:
        if UserModel.objects.filter(username__icontains=value_data).exists():
            raise ValueError('Username exists')
        return value_data
```
##  `from_orm(cls, obj: Any)`
You can generate a schema instance from your django model instance
```Python
from typings import Optional
from django.contrib.auth import get_user_model
from ninja_schema import ModelSchema, model_validator

UserModel = get_user_model()
new_user = UserModel.objects.create_user(
    username='eadwin', email='eadwin@example.com', 
    password='password', first_name='Emeka', last_name='Okoro'
)


class UserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ['id','first_name', 'last_name', 'username', 'email']

schema = UserSchema.from_orm(new_user)
print(schema.json(indent=2)
{
    "id": 1,
    "first_name": "Emeka",
    "last_name": "Okoro",
    "email": "eadwin@example.com",
    "username": "eadwin",
}
```

## `apply(self, model_instance, **kwargs)`
You can transfer data from your ModelSchema to Django Model instance using the `apply` function.
The `apply` function uses Pydantic model `.dict` function, `dict` function filtering that can be passed as `kwargs` to the `.apply` function.

For more info, visit [Pydantic model export](https://pydantic-docs.helpmanual.io/usage/exporting_models/)
```Python
from typings import Optional
from django.contrib.auth import get_user_model
from ninja_schema import ModelSchema, model_validator

UserModel = get_user_model()
new_user = UserModel.objects.create_user(username='eadwin', email='eadwin@example.com', password='password')


class UpdateUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ['first_name', 'last_name', 'username']
        optional = ['username']  # `username` is now optional

schema = UpdateUserSchema(first_name='Emeka', last_name='Okoro')
schema.apply(new_user, exclude_none=True)

assert new_user.first_name == 'Emeka' # True
assert new_user.username == 'eadwin' # True
```

## Generated Schema Sample

```Python
from django.contrib.auth import get_user_model
from ninja_schema import ModelSchema, model_validator

UserModel = get_user_model()


class UserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = '__all__'
        depth = 2

        
print(UserSchema.schema())

{
    "title": "UserSchema",
    "type": "object",
    "properties": {
        "id": {"title": "Id", "extra": {}, "type": "integer"},
        "password": {"title": "Password", "maxLength": 128, "type": "string"},
        "last_login": {"title": "Last Login","type": "string", "format": "date-time"},
        "is_superuser": {"title": "Superuser Status",
            "description": "Designates that this user has all permissions without explicitly assigning them.",
            "default": false,
            "type": "boolean"
        },
        "username": {
            "title": "Username",
            "description": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "maxLength": 150,
            "type": "string"
        },
        "first_name": {
            "title": "First Name",
            "maxLength": 150,
            "type": "string"
        },
        "last_name": {
            "title": "Last Name",
            "maxLength": 150,
            "type": "string"
        },
        "email": {
            "title": "Email Address",
            "type": "string",
            "format": "email"
        },
        "is_staff": {
            "title": "Staff Status",
            "description": "Designates whether the user can log into this admin site.",
            "default": false,
            "type": "boolean"
        },
        "is_active": {
            "title": "Active",
            "description": "Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
            "default": true,
            "type": "boolean"
        },
        "date_joined": {
            "title": "Date Joined",
            "type": "string",
            "format": "date-time"
        },
        "groups": {
            "title": "Groups",
            "description": "The groups this user belongs to. A user will get all permissions granted to each of their groups.",
            "type": "array",
            "items": {
                "$ref": "#/definitions/Group"
            }
        },
        "user_permissions": {
            "title": "User Permissions",
            "description": "Specific permissions for this user.",
            "type": "array",
            "items": {
                "$ref": "#/definitions/Permission"
            }
        }
    },
    "required": [
        "password",
        "username",
        "groups",
        "user_permissions"
    ],
    "definitions": {
        "Permission": {
            "title": "Permission",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "extra": {},
                    "type": "integer"
                },
                "name": {
                    "title": "Name",
                    "maxLength": 255,
                    "type": "string"
                },
                "content_type_id": {
                    "title": "Content Type",
                    "type": "integer"
                },
                "codename": {
                    "title": "Codename",
                    "maxLength": 100,
                    "type": "string"
                }
            },
            "required": [
                "name",
                "content_type_id",
                "codename"
            ]
        },
        "Group": {
            "title": "Group",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "extra": {},
                    "type": "integer"
                },
                "name": {
                    "title": "Name",
                    "maxLength": 150,
                    "type": "string"
                },
                "permissions": {
                    "title": "Permissions",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Permission"
                    }
                }
            },
            "required": [
                "name",
                "permissions"
            ]
        }
    }
}
```

