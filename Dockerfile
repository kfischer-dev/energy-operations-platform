FROM python:3.14-slim

WORKDIR /app

# Install dependencies separately to improve Docker layer caching.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the image.
COPY . .

EXPOSE 8000

# Listen on all container interfaces so the API is reachable through port mapping.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]