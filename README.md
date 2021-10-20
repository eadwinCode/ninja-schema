![Test](https://github.com/eadwinCode/django-schema/workflows/Test/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-scheme.svg)](https://badge.fury.io/py/django-scheme)
# Django Schema
Django Schema gives more pydantic feature while converting your django models.

 **Key features:**
  - **Custom Field Support**: django-schema converts django model to native pydantic types which gives you quick field validation out of the box. eg Enums, email, IPAddress, URLs
  - **Field Validator**: Fields can be validated with **model_validator** just like pydantic **[validator](https://pydantic-docs.helpmanual.io/usage/validators/)** or **[root_validator](https://pydantic-docs.helpmanual.io/usage/validators/)**. 
  
## Installation

```
pip install django-ninja
```

## Usage

In your django project next to urls.py create new `api.py` file:

```Python
from django.contrib.auth import get_user_model
from django_schema import ModelSchema, model_validator

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

## Field Validation
**model_validator** is a substitute for **pydantic [validator](https://pydantic-docs.helpmanual.io/usage/validators/)** used for pre and post fields validation.
There functionalities are the same. More info [pydantic validators](https://pydantic-docs.helpmanual.io/usage/validators/)
```Python
from django.contrib.auth import get_user_model
from django_schema import ModelSchema, model_validator

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

## Configuration Properties
- **model**: Django Model
- **include**: Fields to include, `default: '__all__'`
- **exclude**: Fields to exclude, `default: set()`
- **optional**: Fields to mark optional,` default: set()`
`optional = '__all__'` will make all schema fields optional 
- **depth**: defines depth to nested generated schema, `default: 0`