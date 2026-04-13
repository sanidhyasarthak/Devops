from dataclasses import dataclass

@dataclass
class RiskConfig:
    max_position_pct: float = 0.10   # max 10% of equity in one symbol
    daily_stop_loss:  float = 0.02   # halt trading if -2% daily equity
    max_open_positions: int = 20
    max_leverage: float = 1.0        # 1x = no leverage (paper trading safe)

class RiskGuard:
    def __init__(self, config: RiskConfig):
        self.cfg = config
        self._daily_start_equity: float | None = None

    def set_daily_start(self, equity: float):
        self._daily_start_equity = equity

    def check_new_order(self, symbol: str, quantity: float,
                        price: float, portfolio_snapshot: dict) -> tuple[bool, str]:
        equity = portfolio_snapshot["total_equity"]
        cost   = quantity * price
        open_count = len(portfolio_snapshot["positions"])
        
        if open_count >= self.cfg.max_open_positions:
            return False, f"Max open positions ({self.cfg.max_open_positions}) reached"
            
        if cost / equity > self.cfg.max_position_pct:
            return False, (f"Order size {cost:.2f} exceeds "
                           f"{self.cfg.max_position_pct*100:.0f}% of equity")
                           
        if self._daily_start_equity:
            daily_loss = (equity - self._daily_start_equity) / self._daily_start_equity
            if daily_loss < -self.cfg.daily_stop_loss:
                return False, (f"Daily stop-loss breached: "
                               f"{daily_loss*100:.2f}% loss today")
                               
        return True, "ok"