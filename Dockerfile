
FROM python:3.11-slim


WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE=1
# prevents Python from buffering stdout/stderr
# so logs appear immediately
ENV PYTHONUNBUFFERED=1

# install system dependencies PostgreSQL needs
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first — Docker layer caching
# if requirements.txt hasn't changed, this layer is cached
# and pip install is skipped on rebuild — much faster
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# copy the rest of the application code
COPY . .

# expose port 8000 to the outside world
EXPOSE 8000

# command to run when container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]