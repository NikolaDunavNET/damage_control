FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* \

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY opticka_analiza_izvestaja.py .
COPY vizualna_anliza_ostecenja.py .
COPY transkripcija_izvestaja.py .
COPY konfiguracija.py .
COPY eu_izvestaj_forma_izlaze.json .
COPY generalna_forma_izlaza.json .


EXPOSE 80

# CMD ["fastapi", "run", "fastapi_app.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]