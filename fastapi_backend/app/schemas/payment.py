"""Payment and deposit schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models import DepositMethod, DepositStatus, WalletTransactionType


class DepositCreate(BaseModel):
    """Create a simulated deposit request."""

    method: DepositMethod
    amount_kes: float = Field(..., ge=50, description="Minimum KSh 50")
    phone_number: Optional[str] = Field(None, max_length=30)
    institution_name: Optional[str] = Field(None, max_length=120)
    account_reference: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = Field(None, max_length=500)


class WithdrawalCreate(BaseModel):
    """Create a wallet withdrawal request."""

    method: DepositMethod
    amount_kes: float = Field(..., ge=50, description="Minimum KSh 50")
    phone_number: Optional[str] = Field(None, max_length=30)
    institution_name: Optional[str] = Field(None, max_length=120)
    account_reference: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = Field(None, max_length=500)


class DepositConfirm(BaseModel):
    """Complete a pending deposit after provider/user confirmation."""

    provider_reference: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = Field(None, max_length=500)


class DepositResponse(BaseModel):
    """Deposit response payload."""

    id: UUID
    user_id: UUID
    method: DepositMethod
    transaction_type: WalletTransactionType
    status: DepositStatus
    amount_kes: float
    reference: str
    provider: Optional[str] = None
    provider_reference: Optional[str] = None
    checkout_url: Optional[str] = None
    provider_status: Optional[str] = None
    phone_number: Optional[str] = None
    institution_name: Optional[str] = None
    account_reference: Optional[str] = None
    notes: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    disclaimer: Optional[str] = None

    class Config:
        from_attributes = True


class DepositListResponse(BaseModel):
    """Deposit history response."""

    deposits: list[DepositResponse]
    disclaimer: str
