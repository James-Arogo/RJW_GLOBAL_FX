"""Deposit and wallet funding endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.schemas.payment import DepositConfirm, DepositCreate, DepositListResponse, DepositResponse, WithdrawalCreate
from app.services.payment_service import PaymentService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/deposits", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: DepositCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a simulated deposit and credit the user's wallet."""
    deposit = await PaymentService.create_deposit(db, current_user, deposit_data)
    response = DepositResponse.model_validate(deposit)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    return response


@router.post("/withdrawals", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a simulated withdrawal to M-Pesa or bank."""
    try:
      withdrawal = await PaymentService.create_withdrawal(db, current_user, withdrawal_data)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

    response = DepositResponse.model_validate(withdrawal)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    return response


@router.post("/deposits/{deposit_id}/confirm", response_model=DepositResponse)
async def confirm_deposit(
    deposit_id: str,
    confirm_data: DepositConfirm,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Confirm a pending provider deposit and credit the wallet."""
    deposit = await PaymentService.confirm_deposit(db, current_user, deposit_id, confirm_data)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    response = DepositResponse.model_validate(deposit)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    return response


@router.get("/deposits", response_model=DepositListResponse)
async def get_deposit_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get recent deposit history for the authenticated user."""
    deposits = await PaymentService.list_user_deposits(db, current_user.id, limit)
    response = [DepositResponse.model_validate(item) for item in deposits]
    for item in response:
        item.disclaimer = settings.SIMULATION_DISCLAIMER
    return {"deposits": response, "disclaimer": settings.SIMULATION_DISCLAIMER}
