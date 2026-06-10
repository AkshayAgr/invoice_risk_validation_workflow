import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


INVOICE_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{2,63}$")


class ValidationRequest(BaseModel):
    invoice_number: str = Field(min_length=3, max_length=64)

    @field_validator("invoice_number")
    @classmethod
    def validate_invoice_number(cls, value: str) -> str:
        value = value.strip()
        if not INVOICE_NUMBER_PATTERN.fullmatch(value):
            raise ValueError("invoice_number contains unsupported characters")
        return value


class FinalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_number: str | None
    decision_status: Literal["APPROVE", "APPROVE_WITH_DEDUCTION", "HOLD_FOR_REVIEW", "REJECT", "ESCALATE"]
    risk_score: float = Field(ge=0, le=100)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    currency: str | None
    invoice_summary: dict[str, Any]
    financial_reconciliation: dict[str, Any]
    decision_rationale: dict[str, Any]
    risk_flags: list[str]


class ValidationResponse(BaseModel):
    request_id: str
    invoice_number: str
    result: FinalDecision
    foundry_response_id: str | None = None


class ErrorResponse(BaseModel):
    error: str
    request_id: str
