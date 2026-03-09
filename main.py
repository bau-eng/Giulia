from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connessione PostgreSQL
conn = psycopg2.connect(
    dbname="smart_parking",
    user="postgres",
    password="mS@Gkph#tsqmyY6K76dd",
    host="localhost",
    port="5432"
)

# Funzione distanza in metri
def distanza_metri(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

# Endpoint per parcheggi vicini
@app.get("/parcheggi/vicini")
def parcheggi_vicini(lat: float = Query(...), lng: float = Query(...), raggio: int = 50):
    with conn.cursor() as cur:
        cur.execute("SELECT id, citta, via, lat, lng, stato, tipo, descrizione FROM parcheggi")
        parcheggi = cur.fetchall()

    risultati = []
    for p in parcheggi:
        d = distanza_metri(lat, lng, p[3], p[4])
        if d <= raggio:
            risultati.append({
                "id": p[0],
                "citta": p[1],
                "via": p[2],
                "lat": p[3],
                "lng": p[4],
                "stato": p[5],
                "tipo": p[6],
                "descrizione": p[7],
                "distanza_m": round(d, 1)
            })

    risultati.sort(key=lambda x: x["distanza_m"])
    return {"parcheggi": risultati}

# Endpoint per aggiornare stato parcheggio
@app.post("/aggiorna")
def aggiorna_parcheggio(data: dict):
    with conn.cursor() as cur:
        cur.execute("UPDATE parcheggi SET stato=%s WHERE id=%s", (data["stato"], data["id"]))
        conn.commit()
    return {"ok": True}