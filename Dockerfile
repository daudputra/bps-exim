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

COPY . /app

ENV PATH="/app/venv/bin:$PATH"

ENTRYPOINT ["python", "main.py", "--headless"]
# ENTRYPOINT ["/app/.venv/bin/python", "main.py", "--headless"]





# FROM python:3.11-slim
# WORKDIR /app
# COPY . /app
# # RUN python -m venv venv
# RUN . venv/bin/activate \ 
#     && pip install --no-cache-dir -r requirements.txt \
#     && pip install playwright \ 
#     && playwright install --with-deps
# ENTRYPOINT ["/app/venv/bin/python", "main.py", "--headless"]