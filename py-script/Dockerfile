FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "--workers", "10", "--host", "0.0.0.0", "api:app"]