FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is mounted as a volume — do not COPY it
CMD ["watchfiles", "--filter", "python", "python app.py"]
