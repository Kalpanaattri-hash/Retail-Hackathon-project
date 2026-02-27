from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    generated_sql: str
    data_preview: List[Dict]
    follow_up_questions: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class DashboardOptionsResponse(BaseModel):
    customer_genders: List[str]
    customer_states: List[str]
    product_categories: List[str]


class DashboardChartRequest(BaseModel):
    customer_genders: List[str] = Field(default_factory=list)
    customer_states: List[str] = Field(default_factory=list)
    product_categories: List[str] = Field(default_factory=list)
    selected_dimensions: List[Literal["customer_gender", "customer_state", "product_category_name"]] = Field(
        default_factory=lambda: ["customer_gender", "customer_state", "product_category_name"]
    )
    measure: Literal["sales_value", "sales_quantity"]


class DashboardChart(BaseModel):
    dimension: str
    title: str
    image_base64: str


class DashboardChartResponse(BaseModel):
    measure: str
    charts: List[DashboardChart]
