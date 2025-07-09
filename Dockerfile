FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY opticka_analiza_izvestaja.py .
COPY vizualna_anliza_ostecenja.py .
COPY konfiguracija.py .
COPY eu_izvestaj_forma_izlaze.json .
COPY generalna_forma_izlaza.json .
COPY .env .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]