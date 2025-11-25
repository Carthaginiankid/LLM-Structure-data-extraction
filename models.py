from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Union, List
from datetime import datetime
from enum import Enum
from dateutil import parser as date_parser


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


class Recommendation(BaseModel):
    recommended_supplier: str = Field(..., description="Name of the recommended supplier")
    total_score: float = Field(..., description="Total weighted score of the recommended supplier")
    reasoning: str = Field(..., description="Detailed multi-paragraph reasoning explaining the recommendation with specific metrics and comparisons")
    key_advantages: List[str] = Field(default_factory=list, description="List of 4-6 key advantages with specific metrics")
    considerations: List[str] = Field(default_factory=list, description="List of 3-5 considerations or trade-offs")
    missing_data_impact: Optional[str] = Field(None, description="Note about missing data impact if applicable")


class ExtractedQuotation(BaseModel):
    supplier_name: str = Field(..., description="Supplier company name")
    annual_prices: Dict[int, float] = Field(default_factory=dict, description="Annual prices by year")
    annual_quantities: Dict[int, int] = Field(default_factory=dict, description="Annual quantities by year")
    tooling_cost: Optional[float] = Field(None, description="One-time tooling cost. If renewal/recurring, extract annual amount.")
    tooling_cost_type: Optional[str] = Field(None, description="'one-time' or 'renewal'/'recurring'. If renewal, multiply by years.")
    delivery_terms: Optional[str] = Field(None, description="Delivery terms")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    lead_time: Optional[str] = Field(None, description="Lead time")
    currency: Currency = Field(default=Currency.USD, description="Primary currency")
    quotation_date: Optional[Union[datetime, str]] = Field(None, description="Quotation date (ISO format)")
    moq: Optional[int] = Field(None, description="Minimum Order Quantity")

    @field_validator('quotation_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return date_parser.parse(v)
            except:
                try:
                    return datetime.fromisoformat(v)
                except:
                    return None
        return v
