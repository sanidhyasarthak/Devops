from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

from app.backtester.engine import VectorizedBacktester
from app.backtester.strategies import STRATEGY_REGISTRY
from app.ws.hub import hub

# THIS IS THE LINE UVICORN WAS LOOKING FOR! 👇
app = FastAPI(title="Equity Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your Next.js frontend to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, and OPTIONS
    allow_headers=["*"],
)

# Small Pydantic model to make the route work
class BacktestRequest(BaseModel):
    symbol: str
    start: str
    end: str
    strategy: str
    params: Dict[str, Any] = {}
    initial_capital: float = 100000.0

@app.get("/")
def health_check():
    return {"status": "Engine is running!"}

@app.post("/api/v1/backtest/run")
async def run_backtest(payload: BacktestRequest):
    import pandas as pd
    from sqlalchemy import text
    from app.db.models import engine
    
    # 1. Wrap the query in text()
    query = text(f"""
        SELECT time, open, high, low, close, volume 
        FROM ohlcv 
        WHERE symbol = '{payload.symbol}' 
        AND time >= '{payload.start} 00:00:00' 
        AND time <= '{payload.end} 23:59:59' 
        ORDER BY time ASC
    """)
    
    # 2. Open a direct connection for Pandas
    with engine.connect() as conn:
        ohlcv = pd.read_sql(query, conn, index_col="time")
    
    if ohlcv.empty:
        return {"error": f"No data found for {payload.symbol} in that date range."}
    
    strategy_fn = STRATEGY_REGISTRY[payload.strategy]
    
    from functools import partial
    bound_fn = partial(strategy_fn, **payload.params)
    
    result = VectorizedBacktester(
        initial_capital=payload.initial_capital
    ).run(ohlcv, bound_fn)
    
    return {
        "status": "success",
        "symbol": payload.symbol,
        "strategy": payload.strategy,
        "metrics": result.metrics,
        "equity_curve": result.equity_curve.to_dict()
        
    }

@app.websocket("/ws/portfolio/{account_id}")
async def portfolio_ws(websocket: WebSocket, account_id: str):
    await hub.connect(account_id, websocket)
    
    # --- TEMPORARY LIVE DATA SIMULATOR ---
    # This pumps fake live market data into your frontend to prove the WebSockets work!
    async def mock_market_stream():
        import random
        import asyncio
        current_price = 154.0
        while True:
            current_price += random.uniform(-0.50, 0.50) # Price moves by up to 50 cents a second
            unrealized_pnl = (current_price - 150.0) * 100 # You own 100 shares at $150
            
            snapshot = {
                "cash": 85000.0, 
                "open_pnl": unrealized_pnl, 
                "closed_pnl": 0, 
                "total_equity": 85000.0 + unrealized_pnl,
                "positions": [{
                    "id": "mock_pos_1", "symbol": "AAPL", "quantity": 100, 
                    "entry_price": 150.0, "current_price": current_price, 
                    "unrealized_pnl": unrealized_pnl, "side": "long"
                }]
            }
            await hub.broadcast_snapshot(account_id, snapshot)
            await asyncio.sleep(1) # Wait 1 second and tick again
            
    import asyncio
    task = asyncio.create_task(mock_market_stream())
    # -------------------------------------

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        task.cancel() # Stop the simulation if the user closes the browser
        hub.disconnect(account_id, websocket)