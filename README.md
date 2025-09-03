# Shipment Agent Starter (Python + Spring Boot) — LLM JSON-mode
Set env and run:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r agent_service/requirements.txt
python agent_service/rag.py --rebuild-index
export OPENAI_API_KEY=sk-...; export OPENAI_MODEL=gpt-4o-mini
uvicorn agent_service.app:app --reload --port 8000
```
