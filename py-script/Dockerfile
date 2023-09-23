FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 1323

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "--workers", "10", "api:app"]