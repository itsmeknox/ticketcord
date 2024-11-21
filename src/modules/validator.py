from pydantic import BaseModel
from enum import Enum
from typing import get_origin, get_args, Literal, Union
from functools import wraps

def validate_type(expected_type, value):
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # Handle Enum
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        if value not in expected_type.__members__.values():
            raise ValueError(f"Invalid value '{value}' for Enum '{expected_type.__name__}'")
        return True

    # Handle Optional (Union with NoneType)
    if origin is Union and type(None) in args:
        non_none_type = [arg for arg in args if arg is not type(None)][0]
        return value is None or validate_type(non_none_type, value)

    # Handle List
    if origin is list:
        if not isinstance(value, list):
            raise ValueError(f"Expected a list, got {type(value)}")
        item_type = args[0]
        for item in value:
            validate_type(item_type, item)
        return True

    # Handle Dict
    if origin is dict:
        if not isinstance(value, dict):
            raise ValueError(f"Expected a dict, got {type(value)}")
        key_type, value_type = args
        for key, val in value.items():
            validate_type(key_type, key)
            validate_type(value_type, val)
        return True

    # Handle Literal
    if origin is Literal:
        if value not in args:
            raise ValueError(f"Value '{value}' is not a valid literal {args}")
        return True

    # Default isinstance check for simple types
    if not isinstance(value, expected_type):
        raise ValueError(f"Expected type {expected_type}, got {type(value)}")
    return True

# Decorator for field validation
def validate_fields(model: BaseModel):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate each field in kwargs
            if not kwargs:
                raise ValueError("No fields provided")
            
            for key, value in kwargs.items():
                # Check if the field exists in the model
                if key not in model.model_fields:
                    raise ValueError(f"Invalid field: {key}")

                # Validate the type of the value
                expected_type = model.model_fields[key].annotation
                validate_type(expected_type, value)

            # If all validations pass, call the actual function
            return func(*args, **kwargs)
        return wrapper
    return decorator