"""CRUD endpoints for expenses: create, list (with filters), get, update, delete."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense
from app.schemas import DeleteResponse, ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _get_expense_or_404(expense_id: int, db: Session) -> Expense:
    """Return the expense or raise a 404 HTTP error."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} was not found",
        )
    return expense


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)) -> ExpenseResponse:
    """Create an expense. The `amount` must be greater than zero."""
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("", response_model=list[ExpenseResponse], summary="List expenses")
def list_expenses(
    category: Optional[str] = Query(
        default=None,
        description="Filter by category (case-insensitive).",
        examples=["Food"],
    ),
    start_date: Optional[date] = Query(
        default=None,
        description="Only expenses on or after this date (YYYY-MM-DD).",
        examples=["2026-10-01"],
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Only expenses on or before this date (YYYY-MM-DD).",
        examples=["2026-10-31"],
    ),
    db: Session = Depends(get_db),
) -> list[ExpenseResponse]:
    """Return all expenses, optionally filtered by category and/or date range."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must not be after end_date",
        )

    statement = select(Expense)

    if category is not None and category.strip():
        statement = statement.where(
            func.lower(Expense.category) == category.strip().lower()
        )
    if start_date is not None:
        statement = statement.where(Expense.date >= start_date)
    if end_date is not None:
        statement = statement.where(Expense.date <= end_date)

    statement = statement.order_by(Expense.date.desc(), Expense.id.desc())
    return list(db.scalars(statement).all())


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get a single expense",
)
def get_expense(expense_id: int, db: Session = Depends(get_db)) -> ExpenseResponse:
    """Return one expense by its id, or 404 if it does not exist."""
    return _get_expense_or_404(expense_id, db)


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Replace an expense",
)
def update_expense(
    expense_id: int, expense: ExpenseCreate, db: Session = Depends(get_db)
) -> ExpenseResponse:
    """Replace an existing expense with the submitted values."""
    existing = _get_expense_or_404(expense_id, db)

    for field, value in expense.model_dump().items():
        setattr(existing, field, value)

    db.commit()
    db.refresh(existing)
    return existing


@router.delete(
    "/{expense_id}",
    response_model=DeleteResponse,
    summary="Delete an expense",
)
def delete_expense(expense_id: int, db: Session = Depends(get_db)) -> DeleteResponse:
    """Delete an expense by its id."""
    expense = _get_expense_or_404(expense_id, db)

    db.delete(expense)
    db.commit()
    return DeleteResponse(message="Expense deleted successfully", id=expense_id)
