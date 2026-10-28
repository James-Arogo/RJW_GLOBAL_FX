from models import Trade, db

class ProfitManager:
    def __init__(self, min_profit_margin=0.3):
        self.min_profit_margin = min_profit_margin

    def calculate_platform_profit(self):
        trades = Trade.query.all()
        total_profit = sum(t.profit_loss for t in trades)
        platform_profit = total_profit * self.min_profit_margin
        return round(platform_profit, 2)

    def enforce_margin(self, trade_result):
        trade_result["profit_loss"] *= (1 - self.min_profit_margin)
        return trade_result

profit_manager = ProfitManager()
