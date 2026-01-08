# wishlist
educational project

## 🚀 Docker

Build the image (from project root):

```bash
docker build -t wishlist-app .
```

Run the container (Linux / macOS):

```bash
docker run --rm -p 8000:8000 wishlist-app
```

Run the container (PowerShell on Windows):

```powershell
docker run --rm -p 8000:8000 -v ${PWD}:/app wishlist-app
```

Notes:

- The image installs dependencies from `poetry.lock` / `pyproject.toml` (no virtualenv).
- `alembic/` is excluded via `.dockerignore` and is not copied into the image.
- For local development with live reload, bind-mount the project into `/app` as shown above so `uvicorn --reload` (already used in CMD) sees file changes.
- Ensure `uvicorn` is listed in your `pyproject.toml` dependencies so the container can run the app.

## 🧩 Docker Compose

1. Copy `.env.example` to `.env` and edit credentials if desired:

```bash
cp .env.example .env
```

2. Build and run (detached):

```bash
docker compose up -d --build
```

3. Stop and remove services and volumes:

```bash
docker compose down -v
```

Notes:

- The `db` service uses `postgres:15` and stores data in the `postgres_data` named volume.
- The `app` service mounts the project directory for live reload; remove the mount if you prefer a static image for production.
- The application connects to the database using `DATABASE_URL` pointing to host `db` inside the compose network.
