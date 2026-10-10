"""Automated tests for the Personal Expense Tracker API.

Every test starts with an empty database (see conftest.py), so the tests
can run in any order.
"""

from typing import Any


def expense_payload(**overrides: Any) -> dict[str, Any]:
    """Return a valid expense body, optionally with some fields replaced."""
    payload: dict[str, Any] = {
        "title": "Groceries",
        "amount": 45.5,
        "category": "Food",
        "date": "2026-10-01",
        "note": "Weekly shopping",
    }
    payload.update(overrides)
    return payload


def create_expense(client, **overrides: Any) -> dict[str, Any]:
    """Create an expense and return the JSON response body."""
    response = client.post("/expenses", json=expense_payload(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "running" in body["message"]


def test_interactive_docs_are_available(client):
    response = client.get("/docs")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_create_expense(client):
    response = client.post("/expenses", json=expense_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "Groceries"
    assert body["amount"] == 45.5
    assert body["category"] == "Food"
    assert body["date"] == "2026-10-01"
    assert body["note"] == "Weekly shopping"
    assert body["created_at"]


def test_create_expense_without_optional_note(client):
    payload = expense_payload()
    del payload["note"]

    response = client.post("/expenses", json=payload)

    assert response.status_code == 201
    assert response.json()["note"] is None


def test_create_expense_generates_unique_ids(client):
    first = create_expense(client)
    second = create_expense(client, title="Bus ticket", category="Travel")

    assert second["id"] != first["id"]


def test_create_expense_rejects_zero_amount(client):
    response = client.post("/expenses", json=expense_payload(amount=0))

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"


def test_create_expense_rejects_negative_amount(client):
    response = client.post("/expenses", json=expense_payload(amount=-10.25))

    assert response.status_code == 422


def test_create_expense_rejects_text_amount(client):
    response = client.post("/expenses", json=expense_payload(amount="lots"))

    assert response.status_code == 422


def test_create_expense_rejects_missing_required_field(client):
    payload = expense_payload()
    del payload["amount"]

    response = client.post("/expenses", json=payload)

    assert response.status_code == 422
    assert any(
        error["field"] == "body.amount" for error in response.json()["errors"]
    )


def test_create_expense_rejects_bad_date_format(client):
    response = client.post("/expenses", json=expense_payload(date="01/10/2026"))

    assert response.status_code == 422


def test_create_expense_rejects_blank_title(client):
    response = client.post("/expenses", json=expense_payload(title="   "))

    assert response.status_code == 422


def test_create_expense_rejects_empty_body(client):
    response = client.post("/expenses", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------


def test_list_expenses_starts_empty(client):
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_returns_all(client):
    create_expense(client, title="First", amount=10)
    create_expense(client, title="Second", amount=20)

    response = client.get("/expenses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {item["title"] for item in body}
    assert titles == {"First", "Second"}


def test_get_expense_by_id(client):
    created = create_expense(client)

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "Groceries"


def test_get_expense_not_found(client):
    response = client.get("/expenses/9999")

    assert response.status_code == 404
    assert "9999" in response.json()["detail"]


def test_get_expense_rejects_non_integer_id(client):
    response = client.get("/expenses/not-a-number")

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_update_expense(client):
    created = create_expense(client)
    update = expense_payload(title="Monthly groceries", amount=60.0, category="Food")

    response = client.put(f"/expenses/{created['id']}", json=update)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Monthly groceries"
    assert body["amount"] == 60.0
    assert body["date"] == "2026-10-01"

    stored = client.get(f"/expenses/{created['id']}").json()
    assert stored["title"] == "Monthly groceries"


def test_update_expense_not_found(client):
    response = client.put("/expenses/4242", json=expense_payload())

    assert response.status_code == 404


def test_update_expense_rejects_invalid_amount(client):
    created = create_expense(client)

    response = client.put(
        f"/expenses/{created['id']}", json=expense_payload(amount=-1)
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_expense(client):
    created = create_expense(client)

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert client.get(f"/expenses/{created['id']}").status_code == 404
    assert client.get("/expenses").json() == []


def test_delete_expense_not_found(client):
    response = client.delete("/expenses/7777")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_by_category(client):
    create_expense(client, title="Lunch", category="Food", date="2026-10-02")
    create_expense(client, title="Taxi", category="Travel", date="2026-10-03")

    response = client.get("/expenses", params={"category": "food"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "Food"


def test_filter_by_date_range(client):
    create_expense(client, title="Old", date="2026-09-15")
    create_expense(client, title="In range", date="2026-10-05")
    create_expense(client, title="New", date="2026-11-20")

    response = client.get(
        "/expenses",
        params={"start_date": "2026-10-01", "end_date": "2026-10-31"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "In range"


def test_filter_by_category_and_dates_together(client):
    create_expense(client, title="Food in range", category="Food", date="2026-10-05")
    create_expense(client, title="Travel in range", category="Travel", date="2026-10-06")
    create_expense(client, title="Food out of range", category="Food", date="2026-08-05")

    response = client.get(
        "/expenses",
        params={
            "category": "Food",
            "start_date": "2026-10-01",
            "end_date": "2026-10-31",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Food in range"


def test_filter_returns_empty_list_when_nothing_matches(client):
    create_expense(client, category="Food")

    response = client.get("/expenses", params={"category": "Education"})

    assert response.status_code == 200
    assert response.json() == []


def test_filter_rejects_inverted_date_range(client):
    response = client.get(
        "/expenses",
        params={"start_date": "2026-10-31", "end_date": "2026-10-01"},
    )

    assert response.status_code == 400


def test_filter_rejects_bad_date_format(client):
    response = client.get("/expenses", params={"start_date": "October 2026"})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------


def test_summary_is_zero_for_empty_database(client):
    response = client.get("/summary")

    assert response.status_code == 200
    assert response.json() == {"total_amount": 0.0, "total_count": 0}


def test_summary_totals(client):
    create_expense(client, amount=45.5, category="Food")
    create_expense(client, amount=30.0, category="Food")
    create_expense(client, amount=120.0, category="Travel")

    response = client.get("/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_amount"] == 195.5
    assert body["total_count"] == 3


def test_summary_by_category(client):
    create_expense(client, amount=45.5, category="Food")
    create_expense(client, amount=30.0, category="Food")
    create_expense(client, amount=120.0, category="Travel")

    response = client.get("/summary/category")

    assert response.status_code == 200
    body = response.json()
    assert body["total_amount"] == 195.5
    assert body["total_count"] == 3

    categories = {item["category"]: item for item in body["categories"]}
    assert categories["Food"]["total_amount"] == 75.5
    assert categories["Food"]["count"] == 2
    assert categories["Travel"]["total_amount"] == 120.0
    assert categories["Travel"]["count"] == 1

    # Highest spend first.
    assert body["categories"][0]["category"] == "Travel"


def test_summary_by_category_is_empty_for_empty_database(client):
    response = client.get("/summary/category")

    assert response.status_code == 200
    body = response.json()
    assert body["total_amount"] == 0.0
    assert body["total_count"] == 0
    assert body["categories"] == []


def test_summary_monthly(client):
    create_expense(client, amount=45.5, category="Food", date="2026-10-05")
    create_expense(client, amount=120.0, category="Travel", date="2026-10-20")
    create_expense(client, amount=99.0, category="Shopping", date="2026-09-30")
    create_expense(client, amount=50.0, category="Food", date="2027-01-10")

    response = client.get("/summary/monthly", params={"year": 2026, "month": 10})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "year": 2026,
        "month": 10,
        "total_amount": 165.5,
        "total_count": 2,
    }


def test_summary_monthly_with_no_expenses_returns_zeros(client):
    create_expense(client, date="2026-10-05")

    response = client.get("/summary/monthly", params={"year": 2025, "month": 3})

    assert response.status_code == 200
    assert response.json() == {
        "year": 2025,
        "month": 3,
        "total_amount": 0.0,
        "total_count": 0,
    }


def test_summary_monthly_validates_month(client):
    response = client.get("/summary/monthly", params={"year": 2026, "month": 13})

    assert response.status_code == 422


def test_summary_monthly_requires_parameters(client):
    response = client.get("/summary/monthly")

    assert response.status_code == 422


def test_summaries_use_actual_database_records(client):
    """Creating an expense must change every summary endpoint."""
    create_expense(client, amount=10.0, category="Education", date="2026-10-11")

    overall = client.get("/summary").json()
    by_category = client.get("/summary/category").json()
    monthly = client.get(
        "/summary/monthly", params={"year": 2026, "month": 10}
    ).json()

    assert overall["total_amount"] == 10.0
    assert overall["total_count"] == 1
    assert by_category["categories"][0]["category"] == "Education"
    assert monthly["total_amount"] == 10.0
    assert monthly["total_count"] == 1


# ---------------------------------------------------------------------------
# Unknown routes
# ---------------------------------------------------------------------------


def test_unknown_route_returns_json_404(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Root and Deployment Readiness
# ---------------------------------------------------------------------------


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "online"
    assert "/docs" in body["docs_url"] or body["docs_url"] == "disabled"
    assert body["health_check"] == "/health"


def test_cors_headers_on_requests(client):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ("*", "http://example.com")


def test_app_ui_serves_html(client):
    response = client.get("/app")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "SpendWise" in response.text


def test_browser_accept_header_serves_html(client):
    response = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "SpendWise" in response.text



