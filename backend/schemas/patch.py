from typing import Any, ClassVar

from pydantic import BaseModel, model_validator


class PatchModel(BaseModel):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="before")
    @classmethod
    def reject_null_for_non_nullable_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        invalid_fields = sorted(
            field
            for field in cls.non_nullable_fields
            if field in data and data[field] is None
        )

        if invalid_fields:
            fields = ", ".join(invalid_fields)
            raise ValueError(f"Fields cannot be null: {fields}")

        return data
