FROM python:3.13-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.10
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-dev
COPY apps/api/app ./app
COPY apps/api/migrations ./migrations
COPY apps/api/content ./content
COPY apps/api/alembic.ini ./
RUN useradd --uid 10001 --create-home pakodi && mkdir -p /media && chown pakodi /media
USER 10001
ENV PATH="/app/.venv/bin:$PATH" API_HOST=0.0.0.0 API_PORT=8000 MEDIA_ROOT=/media
EXPOSE 8000
CMD ["python", "-m", "app.serve"]
