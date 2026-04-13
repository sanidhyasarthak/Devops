import uuid
from decimal import Decimal
from datetime import datetime
from app.db.models import Position, db_session

class PortfolioManager:
    def __init__(self, account_id: str, initial_equity: float):
        self.account_id = account_id
        self.cash = Decimal(str(initial_equity))
        self._live_prices: dict[str, Decimal] = {}

    def update_price(self, symbol: str, price: float):
        """Called by the WebSocket price feed on every tick."""
        self._live_prices[symbol] = Decimal(str(price))

    def open_position(self, symbol: str, quantity: float,
                      side: str = "long") -> Position:
        price = self._live_prices.get(symbol)
        if price is None:
            raise ValueError(f"No live price for {symbol}")
        
        cost = price * Decimal(str(quantity))
        self.cash -= cost
        pos = Position(
            id=str(uuid.uuid4()),
            symbol=symbol,
            quantity=Decimal(str(quantity)),
            entry_price=price,
            entry_time=datetime.utcnow(),
            side=side,
            status="open",
            account_id=self.account_id
        )
        with db_session() as s:
            s.add(pos)
        return pos

    def close_position(self, position_id: str) -> dict:
        with db_session() as s:
            pos = s.get(Position, position_id)
            price = self._live_prices[pos.symbol]
            pos.exit_price = price
            pos.exit_time  = datetime.utcnow()
            pos.status     = "closed"
            
            pnl = (price - pos.entry_price) * pos.quantity
            if pos.side == "short":
                pnl = -pnl
            self.cash += pos.entry_price * pos.quantity + pnl
        return {"position_id": position_id, "realized_pnl": float(pnl)}

    def snapshot(self) -> dict:
        """Current portfolio state: cash + open PnL + closed PnL."""
        with db_session() as s:
            open_pos   = s.query(Position).filter_by(
                account_id=self.account_id, status="open").all()
            closed_pos = s.query(Position).filter_by(
                account_id=self.account_id, status="closed").all()
                
        open_pnl = sum(
            (self._live_prices.get(p.symbol, p.entry_price) - p.entry_price)
            * p.quantity * (1 if p.side == "long" else -1)
            for p in open_pos
        )
        closed_pnl = sum(
            (p.exit_price - p.entry_price) * p.quantity
            * (1 if p.side == "long" else -1)
            for p in closed_pos if p.exit_price
        )
        
        total_equity = float(self.cash) + float(open_pnl)
        return {
            "cash":         float(self.cash),
            "open_pnl":     float(open_pnl),
            "closed_pnl":   float(closed_pnl),
            "total_equity": total_equity,
            "positions":    [self._serialize(p) for p in open_pos]
        }

    def _serialize(self, p: Position) -> dict:
        live = self._live_prices.get(p.symbol, p.entry_price)
        pnl  = (live - p.entry_price) * p.quantity * (1 if p.side == "long" else -1)
        return {
            "id": p.id, "symbol": p.symbol,
            "quantity": float(p.quantity),
            "entry_price": float(p.entry_price),
            "current_price": float(live),
            "unrealized_pnl": float(pnl),
            "side": p.side
        }