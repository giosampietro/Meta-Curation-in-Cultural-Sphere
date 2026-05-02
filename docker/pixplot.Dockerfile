FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /work

RUN python -m pip install --upgrade pip wheel \
    && python -m pip install "setuptools<81"

COPY requirements-pixplot.txt /tmp/requirements-pixplot.txt
RUN python -m pip install -r /tmp/requirements-pixplot.txt
