FROM python:3.11

WORKDIR /app

# Копируем requirements из корня проекта
COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY .. .

# Рабочая директория для Django
WORKDIR /app/marketplace

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]