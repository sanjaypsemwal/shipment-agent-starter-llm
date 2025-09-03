import os, json
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from typing import List, Dict, Any
from .schemas import AgentRequest, AgentResponse, Action
from .policy import SYSTEM_PROMPT, TOOLS_DESCRIPTION
from .tools import TOOLS
from .llm_openai import OpenAIModelProvider
app = FastAPI(title="Shipment Agent Service")
class BaseModelProvider:
    def infer_action(self, messages: List[Dict[str,str]], tool_specs: List[Dict[str,Any]])->Action: raise NotImplementedError
class HeuristicModel(BaseModelProvider):
    def infer_action(self, messages, tool_specs):
        user=next((m for m in reversed(messages) if m["role"]=="user"), {"content":""}); text=user["content"].lower()
        if "ord-" in text:
            import re; m=re.search(r"ord-\d+", text); order_id=m.group(0).upper() if m else "ORD-1001"
            return Action(type="use_tool", tool="get_order_status", args={"order_id":order_id})
        return Action(type="use_tool", tool="rag_search", args={"query":user["content"]})
MODEL: BaseModelProvider = OpenAIModelProvider() if os.getenv("OPENAI_API_KEY") else HeuristicModel()
def validate_args(schema: Dict[str,Any], args: Dict[str,Any])->bool:
    return set(schema.get("required",[])).issubset(args.keys())
@app.post("/agent/run", response_model=AgentResponse, response_class=ORJSONResponse)
async def run_agent(req: AgentRequest):
    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"system","content":json.dumps({"tools":TOOLS_DESCRIPTION})},{"role":"user","content":req.goal}]
    obs: Dict[str,Any]={}
    for step in range(req.max_steps):
        try: action=MODEL.infer_action(messages, TOOLS_DESCRIPTION)
        except ValidationError as e: raise HTTPException(status_code=400, detail=str(e))
        if action.type=="final": return AgentResponse(answer=action.final_answer or "", steps=step+1, sources=obs.get("sources"))
        if action.type=="ask_user": return AgentResponse(follow_up=True, question=action.final_answer or "Need more info.", steps=step+1)
        if action.type=="use_tool":
            tool=TOOLS.get(action.tool or ""); 
            if not tool or not validate_args(tool["schema"], action.args or {}): continue
            try: result=tool["fn"](**(action.args or {}))
            except Exception as e: result={"error":str(e)}
            if action.tool=="get_order_status" and "error" not in result:
                answer=f"Order {result['order_id']} via {result['carrier']} is '{result['status']}' near {result['last_location']}. ETA {result['eta']}."
                obs["sources"]=[{"title":"orders.json","quote":f"tracking {result['tracking_number']}"}]
                return AgentResponse(answer=answer, steps=step+1, sources=obs.get("sources"))
            if action.tool=="rag_search" and result.get("results"):
                top=result["results"][0]; obs["sources"]=[{"title":top["title"],"quote":top["quote"]}]
                return AgentResponse(answer=f"According to {top['title']}: {top['quote']}", steps=step+1, sources=obs.get("sources"))
    return AgentResponse(answer="I hit my step limit. Please refine your request.", steps=req.max_steps)
