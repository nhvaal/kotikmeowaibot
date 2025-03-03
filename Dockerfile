# Базовый образ с Python
FROM python:3.9

# Устанавливаю рабочую директорию внутри контейнера
WORKDIR /app

# Копирую файлы проекта в контейнер
COPY . /app

# Устанавливаю зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаю бота
CMD ["python", "botik.py"]