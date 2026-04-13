import json
from fastapi import WebSocket
from collections import defaultdict

class BroadcastHub:
    def __init__(self):
        self._sockets: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, account_id: str, ws: WebSocket):
        await ws.accept()
        self._sockets[account_id].append(ws)

    def disconnect(self, account_id: str, ws: WebSocket):
        self._sockets[account_id].remove(ws)

    async def broadcast_snapshot(self, account_id: str, data: dict):
        dead = []
        for ws in self._sockets.get(account_id, []):
            try:
                await ws.send_text(json.dumps({"type": "snapshot", **data}))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(account_id, ws)

hub = BroadcastHub()