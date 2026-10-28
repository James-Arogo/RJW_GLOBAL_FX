"""Risk and margin calculations for simulated leveraged positions."""

from dataclasses import dataclass


@dataclass
class PositionMetrics:
    """Computed metrics for a leveraged position."""

    leverage: float
    margin_required_kes: float
    notional_value_kes: float
    quantity_units: float
    liquidation_price: float
    unrealized_pnl_kes: float = 0.0
    unrealized_pnl_percent: float = 0.0
    current_price: float | None = None


class RiskEngine:
    """Small utility for margin, liquidation, and unrealized P&L."""

    @staticmethod
    def calculate_position(
        open_price: float,
        margin_kes: float,
        leverage: float,
        direction: str,
        maintenance_margin_ratio: float,
        current_price: float | None = None,
    ) -> PositionMetrics:
        leverage = max(float(leverage or 1.0), 1.0)
        margin_kes = max(float(margin_kes or 0.0), 0.0)
        open_price = max(float(open_price or 0.0), 0.000001)

        notional_value_kes = margin_kes * leverage
        quantity_units = notional_value_kes / open_price if open_price else 0.0
        maintenance_buffer_kes = margin_kes * max(float(maintenance_margin_ratio or 0.0), 0.05)
        liquidation_move = maintenance_buffer_kes / quantity_units if quantity_units else 0.0

        is_long = direction == "long"
        liquidation_price = open_price - liquidation_move if is_long else open_price + liquidation_move

        unrealized_pnl_kes = 0.0
        if current_price is not None and quantity_units:
            price_delta = float(current_price) - open_price
            unrealized_pnl_kes = price_delta * quantity_units if is_long else (-price_delta) * quantity_units

        unrealized_pnl_percent = (unrealized_pnl_kes / margin_kes) * 100 if margin_kes else 0.0

        return PositionMetrics(
            leverage=round(leverage, 2),
            margin_required_kes=round(margin_kes, 2),
            notional_value_kes=round(notional_value_kes, 2),
            quantity_units=round(quantity_units, 8),
            liquidation_price=round(liquidation_price, 6),
            unrealized_pnl_kes=round(unrealized_pnl_kes, 2),
            unrealized_pnl_percent=round(unrealized_pnl_percent, 2),
            current_price=round(float(current_price), 6) if current_price is not None else None,
        )
