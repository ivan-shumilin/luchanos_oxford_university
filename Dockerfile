ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# Add PostgreSQL APT repository for specific versions
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends wget gnupg2 && \
    wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client-15 \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
WORKDIR .

# pip & requirements
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Execute
CMD ["python", "main.py"]
