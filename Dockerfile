FROM python:3.14-alpine

WORKDIR app/

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]