FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["/bin/sh", "-c", "python load_csv_data.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
