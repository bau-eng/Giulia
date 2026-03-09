import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import urllib.parse

app = FastAPI()

# Consenti al frontend di fare richieste al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puoi restringere al tuo dominio se vuoi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Connessione al database Postgres su Render
# -------------------------------------------------

# Prendi l'URL dal variabile d'ambiente (configurata su Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("Imposta la variabile d'ambiente DATABASE_URL su Render!")

# Parse URL per psycopg2
result = urllib.parse.urlparse(DATABASE_URL)

db_user = result.username
db_password = result.password
db_name = result.path[1:]  # togli la barra iniziale
db_host = result.hostname
db_port = result.port

# connessione al database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# -------------------------------------------------
# Route demo per parcheggi
# -------------------------------------------------
@app.get("/parcheggi/vicini")
async def parcheggi_vicini(lat: float, lng: float, raggio: float):
    cur = conn.cursor()
    # esempio semplice: prendi tutti i parcheggi entro raggio
    cur.execute("SELECT lat, lng, stato, tipo, descrizione FROM parcheggi;")
    rows = cur.fetchall()
    parcheggi = []
    for r in rows:
        parcheggi.append({
            "lat": r[0],
            "lng": r[1],
            "stato": r[2],
            "tipo": r[3],
            "descrizione": r[4]
        })
    cur.close()
    return {"parcheggi": parcheggi}