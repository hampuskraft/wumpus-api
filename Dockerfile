FROM python:3.11-alpine AS builder
RUN apk add --no-cache gcc git python3-dev musl-dev linux-headers
WORKDIR /app
RUN python -m venv /app/.venv
COPY requirements.txt /app/
RUN /app/.venv/bin/pip install -r requirements.txt

FROM python:3.11-alpine
RUN mkdir /app && chown -R 65534:65534 /app
WORKDIR /app
USER nobody
COPY --chown=65534:65534 --from=builder /app/.venv /app/.venv
COPY --chown=65534:65534 wumpus /app/wumpus
CMD /app/.venv/bin/gunicorn -b 0.0.0.0:8080 -k gevent wumpus.main:app
EXPOSE 8080
