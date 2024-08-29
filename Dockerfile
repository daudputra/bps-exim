# FROM python:3.12.1-slim

# WORKDIR /app

# COPY requirements.txt ./

# RUN python -m venv .venv && \
#     . .venv/bin/activate && \
#     pip install --no-cache-dir -r requirements.txt && \
#     pip install playwright && \
#     playwright install --with-deps

# COPY . /app

# CMD ["/app/.venv/bin/python", "main.py", "--headless"]

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./

RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /app/.venv/bin/pip install playwright && \
    /app/.venv/bin/playwright install --with-deps

COPY . /app

ENTRYPOINT ["/app/.venv/bin/python", "main.py", "--headless"]