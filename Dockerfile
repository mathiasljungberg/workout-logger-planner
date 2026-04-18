FROM node:22-alpine AS web-build
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json* ./apps/web/
RUN cd apps/web && npm install
COPY apps/web ./apps/web
RUN cd apps/web && npm run build

FROM python:3.12-slim AS api-build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY apps/api/pyproject.toml ./apps/api/
RUN pip install --no-cache-dir --upgrade pip && cd apps/api && pip install --no-cache-dir .
COPY apps/api ./apps/api
COPY --from=web-build /app/apps/web/dist ./apps/api/app/static
WORKDIR /app/apps/api
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:10000", "app.main:app"]

