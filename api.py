import json
import logging
import sqlite3
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Connexion à la base de données SQLite3
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SENSOR (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        status INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS HISTORY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id INTEGER NOT NULL,
        temperature FLOAT,
        humidity FLOAT,
        battery_level INTEGER,
        signal_rssi FLOAT,
        update_time DATETIME,
        FOREIGN KEY (sensor_id) REFERENCES Sensor(id) ON DELETE CASCADE
    );
''')
conn.commit()

def convert_date(date: str) -> str:
    """
    Convertit une date au format '%a, %d %b %Y %H:%M:%S GMT' en format ISO '%Y-%m-%d %H:%M:%S'.

    Parameters:
    - date (str): La date au format '%a, %d %b %Y %H:%M:%S GMT'.

    Returns:
    - str: La date convertie au format ISO '%Y-%m-%d %H:%M:%S'.
    """
    date_object = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT')
    iso_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
    return iso_date  

def get_web_service():
    """
    Récupère les données du service web externe, les transforme et les sauvegarde localement.

    Parameters:
    - limit (int): Le nombre maximal d'éléments à récupérer.
    - start_date (Optional[str]): La date de début pour filtrer les données (format ISO).
    - end_date (Optional[str]): La date de fin pour filtrer les données (format ISO).

    Returns:
    - List[dict]: La liste des données transformées.
    """
    # Connexion à la base de données SQLite3 à l'intérieur de la fonction
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()

    url = f"http://app.objco.com:8099/?account=MRHAOCUYL2&limit=1"

    datas = requests.get(url)
    datas.encoding
    datas = datas.text
    datas = json.loads(datas)

    # Transformation de chaque élément des datas
    for data in datas:
        exa_code = data[1]
        date = data[2]
        date = convert_date(date)
        
        cursor.execute('SELECT id FROM SENSOR')
        list_capteurs = ["6218223","06190485","62190434"]
        
        for capteur in list_capteurs :
            if capteur in exa_code :
                tag_info_index = exa_code.index(capteur)
                tag_info = exa_code[tag_info_index:tag_info_index+22]

                id_capteur = tag_info[0:7]
                
                name = f"sensor-{id_capteur}"

                status = int(tag_info[8:10], 16)

                battery = int(tag_info[10:14], 16)
                battery = battery / 1000
                battery = (battery - 3.32) // 0.083

                temperature = int(tag_info[14:18], 16) / 10

                humidity = int(tag_info[18:20], 16)
                if humidity == 255:
                    humidity = None

                rssi_signal = int(tag_info[20:22], 16)

                sensor_type = 1  # Température
                name = f"Temp-{id_capteur}"
                logging.info("La tâche s'est exécutée!")
                
                cursor.execute("INSERT INTO HISTORY (sensor_id, temperature, humidity, battery_level, signal_rssi, update_time) "
                                "VALUES (?, ?, ?, ?, ?, ?)",
                                (id_capteur, temperature, humidity, battery, rssi_signal, date))

        # N'oubliez pas de fermer la connexion
        conn.commit()
        conn.close()

# Créer une instance de l'ordonnanceur
scheduler = AsyncIOScheduler()

# Tâche de fond pour appeler get_web_service toutes les 5 minutes
def update_data():
    get_web_service()

# Planifier la tâche de fond pour s'exécuter toutes les 5 minutes
scheduler.add_job(update_data, 'interval', minutes=5)

# Endpoint pour récupérer tous les éléments
@app.get("/")
async def main():
    try:
        # Récupération de tous les éléments depuis la base de données
        cursor.execute('SELECT * FROM HISTORY')
        items = cursor.fetchall()

        # Conversion des résultats en liste de dictionnaires
        items_list = [{"id capteur": row[1], "temperature": row[2], "humidity": row[3],"battery": row[4], "signal rssi": row[5], "date": row[6]} for row in items]

        return items_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour forcer une mise à jour immédiate
@app.get("/force-update")
async def force_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_web_service)
    return {"message": "Mise à jour forcée en cours"}

# Au démarrage, démarrer l'ordonnanceur
@app.on_event("startup")
def startup_event():
    scheduler.start()

# Fermeture de la connexion à la base de données lors de l'arrêt de l'application
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    conn.close()