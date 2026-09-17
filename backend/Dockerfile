# MiniPay API image: python:3.12-slim, non-root, pinned deps, HEALTHCHECK.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user (uid 10001).
RUN useradd -r -u 10001 app && chown -R app /srv
USER app

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s CMD \
  python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
