# Use Python 3.11
FROM python:3.11-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie requirements e instale
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie todo o código
COPY . .

# Exponha a porta do FastAPI
EXPOSE 8000

# Comando para rodar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
