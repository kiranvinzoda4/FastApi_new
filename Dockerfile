FROM python:3.10.4

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml poetry.lock* /

# Install dependencies
RUN poetry install --only=main --no-dev

COPY ./alembic.ini /
RUN mkdir /app
COPY ./app/ /app/

CMD alembic upgrade head ; uvicorn app.main:app --host 0.0.0.0 --port 8000
