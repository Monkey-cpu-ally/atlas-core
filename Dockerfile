FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app:/app/backend

ARG INSTALL_TOOL_EXTRAS=false

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
COPY backend/requirements-tools.txt /app/backend/requirements-tools.txt
RUN python -m pip install --upgrade pip \
    && pip install -r /app/backend/requirements.txt \
    && if [ "$INSTALL_TOOL_EXTRAS" = "true" ]; then pip install -r /app/backend/requirements-tools.txt; fi

COPY . /app

WORKDIR /app/backend

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
