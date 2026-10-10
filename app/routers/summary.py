"""Summary endpoints: totals, per-category breakdown and monthly totals."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense
from app.schemas import (
    CategorySummaryResponse,
    CategoryTotal,
    MonthlySummaryResponse,
    SummaryResponse,
)

router = APIRouter(prefix="/summary", tags=["summary"])


def _totals(db: Session) -> tuple[float, int]:
    """Return (total_amount, total_count) for the whole expenses table.

    An empty table returns (0.0, 0) instead of None.
    """
    amount = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0.0)))
    count = db.scalar(select(func.count(Expense.id)))
    return round(float(amount or 0.0), 2), int(count or 0)


@router.get("", response_model=SummaryResponse, summary="Overall spending summary")
def spending_summary(db: Session = Depends(get_db)) -> SummaryResponse:
    """Return the total amount spent and the total number of expenses."""
    total_amount, total_count = _totals(db)
    return SummaryResponse(total_amount=total_amount, total_count=total_count)


@router.get(
    "/category",
    response_model=CategorySummaryResponse,
    summary="Spending grouped by category",
)
def category_summary(db: Session = Depends(get_db)) -> CategorySummaryResponse:
    """Return totals per category, ordered by the highest spend first."""
    rows = db.execute(
        select(
            Expense.category,
            func.sum(Expense.amount),
            func.count(Expense.id),
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    categories = [
        CategoryTotal(
            category=category,
            total_amount=round(float(total or 0.0), 2),
            count=int(count or 0),
        )
        for category, total, count in rows
    ]

    total_amount = round(sum(item.total_amount for item in categories), 2)
    total_count = sum(item.count for item in categories)

    return CategorySummaryResponse(
        total_amount=total_amount,
        total_count=total_count,
        categories=categories,
    )


@router.get(
    "/monthly",
    response_model=MonthlySummaryResponse,
    summary="Spending for one month",
)
def monthly_summary(
    year: int = Query(..., ge=1900, le=9999, description="Year, e.g. 2026"),
    month: int = Query(..., ge=1, le=12, description="Month, from 1 to 12"),
    db: Session = Depends(get_db),
) -> MonthlySummaryResponse:
    """Return totals for a given year and month. Empty months return zeros."""
    statement = (
        select(
            func.coalesce(func.sum(Expense.amount), 0.0),
            func.count(Expense.id),
        )
        .where(extract("year", Expense.date) == year)
        .where(extract("month", Expense.date) == month)
    )
    total, count = db.execute(statement).one()

    return MonthlySummaryResponse(
        year=year,
        month=month,
        total_amount=round(float(total or 0.0), 2),
        total_count=int(count or 0),
    )
