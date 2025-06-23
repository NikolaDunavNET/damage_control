FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY fastapi_app.py geminitest.py ./

EXPOSE 80

# CMD ["fastapi", "run", "fastapi_app.py"]
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "80"]