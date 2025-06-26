FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py opticka_analiza_izvestaja.py vizualna_anliza_ostecenja.py transkripcija_izvestaja.py konfiguracija.py ./

EXPOSE 80

# CMD ["fastapi", "run", "fastapi_app.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]