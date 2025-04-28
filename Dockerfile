FROM python:3.11-slim

WORKDIR /app

# 1) install dependencies from api/requirements.txt
COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) copy the api source
COPY api/ api/

# 3) ensure Python will find /app/api
ENV PYTHONPATH=/app

# 4) launch the FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]