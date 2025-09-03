import json
from pathlib import Path
from typing import Dict, Any
DATA_ORDERS = Path(__file__).resolve().parents[1] / "data" / "orders.json"
from .rag import SimpleRAG
_rag_cache=None
def rag_search(query:str)->Dict[str,Any]:
    global _rag_cache
    if _rag_cache is None: _rag_cache=SimpleRAG(); _rag_cache.load()
    return {"results": _rag_cache.search(query)}
def get_order_status(order_id:str)->Dict[str,Any]:
    orders=json.loads(DATA_ORDERS.read_text(encoding="utf-8"))
    for o in orders:
        if o["order_id"].lower()==order_id.lower():
            return {"order_id":o["order_id"],"carrier":o["carrier"],"tracking_number":o["tracking_number"],"status":o["status"],"last_location":o["last_location"],"eta":o["eta"],"history":o["history"],"source":"orders.json"}
    return {"error": f"Order {order_id} not found"}
TOOLS={
    "rag_search":{"fn":rag_search,"schema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
    "get_order_status":{"fn":get_order_status,"schema":{"type":"object","properties":{"order_id":{"type":"string"}},"required":["order_id"]}},
}
