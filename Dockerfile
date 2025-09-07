# Arquivo de comandos p/ criar a imagem Docker da aplicação

# imagem base
FROM python:3.12-slim

# p/ manter o container enxuto
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
	PYTHONPATH=/app

# diretório de trabalho
WORKDIR /app

# deps nativos (compilar algumas libs)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# instala as libs do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copie o código
COPY . .

EXPOSE 8000
