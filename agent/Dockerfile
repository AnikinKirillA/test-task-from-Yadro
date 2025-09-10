FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем Python 3, venv, pip и системные утилиты
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-venv python3-pip sshpass curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создаём виртуальное окружение для Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Обновляем pip внутри venv и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем тесты
COPY tests /app/tests

# Запуск тестов по умолчанию
CMD ["pytest", "-v", "-s"]

ENV PYTHONUNBUFFERED=1