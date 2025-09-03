FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/agent_service
COPY ../data /app/data
EXPOSE 8000
ENV OPENAI_MODEL=gpt-4o-mini
CMD ["uvicorn", "agent_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
