# Базовый образ Python
FROM python:3.12-slim

# Чтобы логи сразу печатались в консоль
ENV PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем только файлы зависимостей (для кеша слоёв)
COPY pyproject.toml poetry.lock* /app/

# Ставим зависимости в системный python внутри контейнера (без virtualenv)
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Копируем код проекта
COPY . /app

EXPOSE 8000

# Запуск Django (dev)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
