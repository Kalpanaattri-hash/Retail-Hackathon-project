import base64
import io
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    DashboardChart,
    DashboardChartRequest,
    DashboardChartResponse,
    DashboardOptionsResponse,
)

matplotlib.use("Agg")

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DIMENSION_LABELS = {
    "customer_gender": "Customer Gender",
    "customer_state": "Customer State",
    "product_category_name": "Product Category",
}


def _get_distinct_values(db: Session, column_name: str) -> list[str]:
    query = text(
        f"""
        SELECT DISTINCT {column_name}
        FROM olist_master_sales
        WHERE {column_name} IS NOT NULL
        ORDER BY {column_name}
        """
    )
    rows = db.execute(query).fetchall()
    return [str(row[0]) for row in rows if row[0] is not None and str(row[0]).strip()]


def _build_where_clause(payload: DashboardChartRequest) -> tuple[str, dict[str, Any]]:
    filters = [
        ("customer_gender", payload.customer_genders),
        ("customer_state", payload.customer_states),
        ("product_category_name", payload.product_categories),
    ]

    conditions: list[str] = []
    params: dict[str, Any] = {}

    for column_name, values in filters:
        if not values:
            continue

        placeholders: list[str] = []
        for index, value in enumerate(values):
            param_key = f"{column_name}_{index}"
            placeholders.append(f":{param_key}")
            params[param_key] = value

        conditions.append(f"{column_name} IN ({', '.join(placeholders)})")

    if not conditions:
        return "", params

    return f"WHERE {' AND '.join(conditions)}", params


@router.get("/options", response_model=DashboardOptionsResponse)
def dashboard_options(db: Session = Depends(get_db)) -> DashboardOptionsResponse:
    return DashboardOptionsResponse(
        customer_genders=_get_distinct_values(db, "customer_gender"),
        customer_states=_get_distinct_values(db, "customer_state"),
        product_categories=_get_distinct_values(db, "product_category_name"),
    )


@router.post("/charts", response_model=DashboardChartResponse)
def dashboard_charts(payload: DashboardChartRequest, db: Session = Depends(get_db)) -> DashboardChartResponse:
    measure_column = "order_sale_value" if payload.measure == "sales_value" else "order_items_qty"
    where_clause, params = _build_where_clause(payload)

    selected_dimensions = payload.selected_dimensions or [
        "customer_gender",
        "customer_state",
        "product_category_name",
    ]

    sns.set_theme(style="whitegrid")

    charts: list[DashboardChart] = []

    for dimension in selected_dimensions:
        query = text(
            f"""
            SELECT {dimension} AS label, SUM({measure_column}) AS metric
            FROM olist_master_sales
            {where_clause}
            {"AND" if where_clause else "WHERE"} {dimension} IS NOT NULL
            GROUP BY {dimension}
            ORDER BY metric DESC
            LIMIT 12
            """
        )

        rows = db.execute(query, params).fetchall()
        labels = [str(row[0]) for row in rows]
        values = [float(row[1]) for row in rows]

        if not labels:
            continue

        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x=labels, y=values, ax=ax, color="#2563eb")

        ax.set_title(f"{DIMENSION_LABELS[dimension]} by {'Sales Value' if payload.measure == 'sales_value' else 'Sales Quantity'}")
        ax.set_xlabel(DIMENSION_LABELS[dimension])
        ax.set_ylabel("Sales Value" if payload.measure == "sales_value" else "Sales Quantity")
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=120)
        plt.close(fig)
        buffer.seek(0)

        charts.append(
            DashboardChart(
                dimension=dimension,
                title=ax.get_title(),
                image_base64=base64.b64encode(buffer.read()).decode("utf-8"),
            )
        )

    return DashboardChartResponse(
        measure=payload.measure,
        charts=charts,
    )
