"""Pydantic schemas used to validate request bodies and format responses."""

import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    """Body used when creating (POST) or replacing (PUT) an expense."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Groceries"])
    amount: float = Field(..., gt=0, allow_inf_nan=False, examples=[45.5])
    category: str = Field(..., min_length=1, max_length=50, examples=["Food"])
    # The field is called `date`, so the type is written as `datetime.date`
    # to avoid a name clash between the field and the imported type.
    date: datetime.date = Field(..., examples=["2026-10-01"])
    note: Optional[str] = Field(None, max_length=500, examples=["Weekly shopping"])

    @field_validator("title", "category")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        """Reject strings that only contain spaces."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty or contain only whitespace")
        return cleaned

    @field_validator("note")
    @classmethod
    def clean_note(cls, value: Optional[str]) -> Optional[str]:
        """Turn an empty note into None instead of an empty string."""
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ExpenseResponse(BaseModel):
    """Shape of an expense returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: float
    category: str
    date: datetime.date
    note: Optional[str] = None
    created_at: datetime.datetime


class DeleteResponse(BaseModel):
    """Response returned after an expense is deleted."""

    message: str
    id: int


class HealthResponse(BaseModel):
    """Response returned by the health-check endpoint."""

    status: str
    message: str


class SummaryResponse(BaseModel):
    """Overall spending totals."""

    total_amount: float
    total_count: int


class CategoryTotal(BaseModel):
    """Spending for one category."""

    category: str
    total_amount: float
    count: int


class CategorySummaryResponse(BaseModel):
    """Overall totals plus a per-category breakdown."""

    total_amount: float
    total_count: int
    categories: list[CategoryTotal]


class MonthlySummaryResponse(BaseModel):
    """Spending totals for a specific month."""

    year: int
    month: int
    total_amount: float
    total_count: int
