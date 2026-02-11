FROM python:3.11-slim

WORKDIR /app

# system deps for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV AUTO_CREATE_TABLES=0

EXPOSE 8000

CMD ["bash", "-lc", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
