FROM python:3.12-slim

# Install uv packaging tool and server dependencies
RUN pip install --no-cache-dir uv fastapi uvicorn

WORKDIR /app
COPY ../pyproject.toml ./pyproject.toml
COPY . ./backend
ENV PYTHONPATH=/app

# Install dependencies using uv (fast, no-venv)
RUN uv pip install --system fastapi==0.112.0 uvicorn

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
