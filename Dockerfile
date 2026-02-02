FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["uvicorn", "temporal_graph_rag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
