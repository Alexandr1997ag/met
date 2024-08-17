# Используем официальный Python образ в качестве базового
FROM python:3.10-slim

# Устанавливаем рабочий каталог
WORKDIR /app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в рабочий каталог
COPY . .

# Определяем переменную окружения
ENV API_TOKEN=6851079900:AAEcLqzD-o5DLjH1uAgApTwwtn4a5w0AU0I

# Команда для запуска приложения
CMD ["python", "bot6_send_ph.py"]
