from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict
class ToolSpec(BaseModel): name: str; description: str; schema: Dict[str, Any]
class Action(BaseModel): type: Literal["use_tool","final","ask_user"]; tool: Optional[str]=None; args: Optional[Dict[str,Any]]=None; final_answer: Optional[str]=None
class AgentRequest(BaseModel): goal: str = Field(...); max_steps: int = 5
class AgentResponse(BaseModel): answer: Optional[str]=None; follow_up: Optional[bool]=False; question: Optional[str]=None; steps: int; sources: Optional[List[Dict[str,str]]]=None
class RAGDoc(BaseModel): doc_id: int; title: str; text: str
