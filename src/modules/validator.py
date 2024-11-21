from pydantic import BaseModel, create_model
from typing import Optional


def validate_fields(model: BaseModel, strict: bool = False):
    if not strict:
        model = create_model(
            f"Partial{model.__name__}",
            **{field: (Optional[field_type], None) for field, field_type in model.__annotations__.items()}
        )

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not kwargs:
                raise ValueError("No fields provided")
            
            if args:
                raise ValueError("Positional arguments are not allowed")
            
            # Validate kwargs against the model
            validated_data: BaseModel = model(**kwargs)
            
            # Filter out fields that were not passed by the user (exclude default None)
            filtered_data = {
                key: value
                for key, value in validated_data.model_dump(exclude_unset=False).items()
                if key in kwargs
            }
            
            # Pass filtered fields to the wrapped function
            return func(**filtered_data)
        
        return wrapper

    return decorator
