FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./gunicorn.env ./

COPY ./app ./app
COPY ./images ./images
