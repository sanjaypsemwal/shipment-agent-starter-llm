import os, json
from typing import List, Dict, Any
from openai import OpenAI
from .schemas import Action
ACTION_JSON_SCHEMA={
 "name":"Action",
 "schema":{"type":"object","additionalProperties":False,"properties":{
  "type":{"type":"string","enum":["use_tool","final","ask_user"]},
  "tool":{"type":"string"},"args":{"type":"object"},"final_answer":{"type":"string"}
 },"required":["type"]}
}
class OpenAIModelProvider:
    def __init__(self, model: str | None = None, temperature: float = 0.0, timeout: float = 20.0):
        self.client=OpenAI(); self.model=model or os.getenv("OPENAI_MODEL","gpt-4o-mini"); self.temperature=temperature; self.timeout=timeout
    def infer_action(self, messages: List[Dict[str,str]], tool_specs: List[Dict[str,Any]])->Action:
        user_msg=next((m for m in reversed(messages) if m.get("role")=="user"), {"content":""})
        system_msgs=[m for m in messages if m.get("role")=="system"]
        payload=[]
        for m in system_msgs: payload.append({"role":"system","content":[{"type":"input_text","text":m.get("content","")}] })
        payload.append({"role":"system","content":[{"type":"input_text","text":json.dumps({"tools":tool_specs})}]})
        payload.append({"role":"user","content":[{"type":"input_text","text":user_msg.get("content","")}] })
        resp=self.client.responses.create(model=self.model, input=payload, temperature=self.temperature, response_format={"type":"json_schema","json_schema":ACTION_JSON_SCHEMA})
        text=getattr(resp,"output_text",None)
        if not text:
            parts=[]; 
            for item in getattr(resp,"output",[]) or []:
                for c in getattr(item,"content",[]) or []:
                    if getattr(c,"type",None)=="output_text": parts.append(c.text)
            text="".join(parts) if parts else ""
        try: obj=json.loads(text)
        except Exception:
            import re; m=re.search(r"\{.*\}", text, flags=re.S)
            if not m: return Action(type="ask_user", final_answer="I could not parse a valid action. Please rephrase.")
            obj=json.loads(m.group(0))
        return Action.model_validate(obj)
