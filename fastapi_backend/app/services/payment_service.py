"""Services for wallet funding and deposit history."""

from dataclasses import dataclass
from datetime import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import DepositMethod, DepositStatus, DepositTransaction, User, WalletTransactionType
from app.schemas.payment import DepositConfirm, DepositCreate, WithdrawalCreate


@dataclass
class DepositDecision:
    """Provider initiation decision."""

    status: DepositStatus
    provider_status: str
    checkout_url: str | None = None
    provider_reference: str | None = None
    notes: str | None = None


class PaymentService:
    """Business logic for simulated deposits."""

    PROVIDER_BY_METHOD = {
        DepositMethod.MPESA: "Safaricom M-Pesa",
        DepositMethod.BANK: "Bank Transfer",
        DepositMethod.CARD: "Debit/Credit Card",
        DepositMethod.SACCO: "SACCO / Microfinance",
    }

    @staticmethod
    def _reference_for(method: DepositMethod, user: User) -> str:
        prefix = method.value.upper()
        username = user.username[:4].upper().ljust(4, "X")
        return f"{prefix}-{username}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    @staticmethod
    def _normalize_uuid(value):
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                return value
        return value

    @staticmethod
    def _provider_decision(method: DepositMethod, reference: str) -> DepositDecision:
        """Return initiation behavior for the selected provider."""
        if method == DepositMethod.MPESA:
            if settings.PAYMENT_PROVIDER_MODE == "live" and settings.MPESA_SHORTCODE and settings.MPESA_PASSKEY:
                return DepositDecision(
                    status=DepositStatus.PENDING,
                    provider_status="stk_push_sent",
                    provider_reference=f"MPESA-STK-{reference}",
                    notes="M-Pesa STK push initiated. Await callback/confirmation.",
                )
            return DepositDecision(
                status=DepositStatus.ACTION_REQUIRED,
                provider_status="awaiting_mpesa_confirmation",
                provider_reference=f"SIM-MPESA-{reference}",
                notes="Simulated M-Pesa flow: confirm after entering the payment code.",
            )

        if method == DepositMethod.CARD:
            checkout_url = (
                f"{settings.CARD_PROVIDER_CALLBACK_URL.rstrip('/')}/checkout/{reference}"
                if settings.CARD_PROVIDER_CALLBACK_URL
                else f"https://payments.example.test/checkout/{reference}"
            )
            provider_name = settings.CARD_PROVIDER_NAME.lower()
            if settings.PAYMENT_PROVIDER_MODE == "live" and settings.CARD_PROVIDER_SECRET_KEY:
                return DepositDecision(
                    status=DepositStatus.PENDING,
                    provider_status=f"{provider_name}_checkout_created",
                    checkout_url=checkout_url,
                    provider_reference=f"CARD-{reference}",
                    notes=f"{settings.CARD_PROVIDER_NAME} checkout created.",
                )
            return DepositDecision(
                status=DepositStatus.ACTION_REQUIRED,
                provider_status="awaiting_card_authorization",
                checkout_url=checkout_url,
                provider_reference=f"SIM-CARD-{reference}",
                notes="Simulated card payment ready for user confirmation.",
            )

        if method == DepositMethod.BANK:
            return DepositDecision(
                status=DepositStatus.PENDING,
                provider_status="awaiting_bank_transfer",
                provider_reference=f"BANK-{reference}",
                notes="Awaiting manual bank transfer confirmation.",
            )

        return DepositDecision(
            status=DepositStatus.COMPLETED,
            provider_status="credited",
            provider_reference=f"SACCO-{reference}",
            notes="Institution-backed simulator credit applied instantly.",
        )

    @staticmethod
    def _withdrawal_decision(method: DepositMethod, reference: str) -> DepositDecision:
        """Return processing behavior for withdrawal requests."""
        if method == DepositMethod.MPESA:
            return DepositDecision(
                status=DepositStatus.ACTION_REQUIRED if settings.PAYMENT_PROVIDER_MODE != "live" else DepositStatus.PENDING,
                provider_status="awaiting_mpesa_disbursement",
                provider_reference=f"WDR-MPESA-{reference}",
                notes="Withdrawal queued for M-Pesa wallet disbursement.",
            )

        if method == DepositMethod.BANK:
            return DepositDecision(
                status=DepositStatus.PENDING,
                provider_status="awaiting_bank_transfer",
                provider_reference=f"WDR-BANK-{reference}",
                notes="Withdrawal queued for bank transfer review.",
            )

        raise ValueError("Withdrawals are only available to M-Pesa and bank accounts.")

    @staticmethod
    async def create_deposit(db: AsyncSession, user: User, deposit_data: DepositCreate) -> DepositTransaction:
        """Create a deposit request and decide whether it is instant or confirmation-based."""
        provider = PaymentService.PROVIDER_BY_METHOD[deposit_data.method]
        reference = PaymentService._reference_for(deposit_data.method, user)
        decision = PaymentService._provider_decision(deposit_data.method, reference)
        deposit = DepositTransaction(
            user_id=user.id,
            method=deposit_data.method,
            transaction_type=WalletTransactionType.DEPOSIT,
            status=decision.status,
            amount_kes=deposit_data.amount_kes,
            reference=reference,
            provider=provider,
            provider_reference=decision.provider_reference,
            checkout_url=decision.checkout_url,
            provider_status=decision.provider_status,
            phone_number=deposit_data.phone_number.strip() if deposit_data.phone_number else None,
            institution_name=deposit_data.institution_name.strip() if deposit_data.institution_name else None,
            account_reference=deposit_data.account_reference.strip() if deposit_data.account_reference else None,
            notes=(deposit_data.notes.strip() if deposit_data.notes else decision.notes),
            processed_at=datetime.utcnow() if decision.status == DepositStatus.COMPLETED else None,
        )

        db.add(deposit)
        if decision.status == DepositStatus.COMPLETED:
            user.balance_kes = float(user.balance_kes) + float(deposit_data.amount_kes)
        await db.commit()
        await db.refresh(deposit)
        await db.refresh(user)
        return deposit

    @staticmethod
    async def create_withdrawal(db: AsyncSession, user: User, withdrawal_data: WithdrawalCreate) -> DepositTransaction:
        """Create a withdrawal request and reserve balance immediately."""
        if float(user.balance_kes) < float(withdrawal_data.amount_kes):
            raise ValueError("Insufficient balance for withdrawal")

        reference = PaymentService._reference_for(withdrawal_data.method, user)
        decision = PaymentService._withdrawal_decision(withdrawal_data.method, reference)
        provider = PaymentService.PROVIDER_BY_METHOD[withdrawal_data.method]

        withdrawal = DepositTransaction(
            user_id=user.id,
            method=withdrawal_data.method,
            transaction_type=WalletTransactionType.WITHDRAWAL,
            status=decision.status,
            amount_kes=withdrawal_data.amount_kes,
            reference=reference,
            provider=provider,
            provider_reference=decision.provider_reference,
            checkout_url=decision.checkout_url,
            provider_status=decision.provider_status,
            phone_number=withdrawal_data.phone_number.strip() if withdrawal_data.phone_number else None,
            institution_name=withdrawal_data.institution_name.strip() if withdrawal_data.institution_name else None,
            account_reference=withdrawal_data.account_reference.strip() if withdrawal_data.account_reference else None,
            notes=(withdrawal_data.notes.strip() if withdrawal_data.notes else decision.notes),
            processed_at=datetime.utcnow() if decision.status == DepositStatus.COMPLETED else None,
        )

        user.balance_kes = float(user.balance_kes) - float(withdrawal_data.amount_kes)
        db.add(withdrawal)
        await db.commit()
        await db.refresh(withdrawal)
        await db.refresh(user)
        return withdrawal

    @staticmethod
    async def confirm_deposit(
        db: AsyncSession,
        user: User,
        deposit_id,
        confirm_data: DepositConfirm,
    ) -> DepositTransaction:
        """Mark a pending/action-required deposit as completed and credit the wallet."""
        result = await db.execute(
            select(DepositTransaction).where(
                (DepositTransaction.id == PaymentService._normalize_uuid(deposit_id)) & (DepositTransaction.user_id == user.id)
            )
        )
        deposit = result.scalar_one_or_none()
        if not deposit:
            return None

        if deposit.status == DepositStatus.COMPLETED:
            return deposit

        deposit.status = DepositStatus.COMPLETED
        deposit.provider_status = "credited"
        deposit.provider_reference = confirm_data.provider_reference or deposit.provider_reference
        if confirm_data.notes:
            deposit.notes = confirm_data.notes.strip()
        deposit.processed_at = datetime.utcnow()

        if deposit.transaction_type == WalletTransactionType.DEPOSIT:
            user.balance_kes = float(user.balance_kes) + float(deposit.amount_kes)

        await db.commit()
        await db.refresh(deposit)
        await db.refresh(user)
        return deposit

    @staticmethod
    async def list_user_deposits(db: AsyncSession, user_id, limit: int = 20) -> list[DepositTransaction]:
        """Fetch recent deposit history for a user."""
        result = await db.execute(
            select(DepositTransaction)
            .where(DepositTransaction.user_id == user_id)
            .order_by(DepositTransaction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
