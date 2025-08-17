FROM python:3.12-slim

WORKDIR /code

COPY . .

RUN pip install --no-cache-dir -e . --verbose

ENTRYPOINT ["app"]