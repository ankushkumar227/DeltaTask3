FROM python:3.10-slim

# Set environment variables


ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and MySQL connector
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --no-cache-dir mysql-connector-python

COPY server1.py /server1.py

EXPOSE 5050
