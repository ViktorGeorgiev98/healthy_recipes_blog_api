FROM python:3.11-slim

# Set env vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

# Set workdir
WORKDIR /code

# Copy files
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Expose port (not used by Heroku, but good practice)
EXPOSE 8000

# Run server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]