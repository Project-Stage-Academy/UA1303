FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

COPY . .

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]