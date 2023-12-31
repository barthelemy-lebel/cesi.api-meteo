import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

#from alert import is_alert, create_table_alert, maj_alert


app = FastAPI()

# Configurer CORS
origins = ["http://127.0.0.1:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion à la base de données SQLite3
conn = sqlite3.connect('api.db')
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

#create_table_alert()

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
    conn = sqlite3.connect('api.db')
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
        list_capteurs = ["6218223","06190485","06190412"]

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

                name = f"Capteur-{id_capteur}"
                logging.info("La tâche s'est exécutée!")

                cursor.execute("INSERT INTO HISTORY (sensor_id, temperature, humidity, battery_level, signal_rssi, update_time) "
                                "VALUES (?, ?, ?, ?, ?, ?)",
                                (id_capteur, temperature, humidity, battery, rssi_signal, date))

                cursor.execute("INSERT INTO SENSOR (id, name, status) "
                                "VALUES (?, ?, ?)",
                                (id_capteur, name, status))

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
async def main(start_date: Optional[str] = None, end_date: Optional[str] = None, sensor_id: Optional[int] = None):
    """
    Récupère les données stockées dans la base de données.

    Parameters:
    - start_date (Optional[str]): La date de début pour filtrer les données (format ISO).
    - end_date (Optional[str]): La date de fin pour filtrer les données (format ISO).
    - sensor_id (Optional[int]): L'ID du capteur pour filtrer les données d'un capteur spécifique.

    Returns:
    - List[SensorData]: La liste des données récupérées.
    """
    try:
        query = 'SELECT HISTORY.*, SENSOR.name FROM HISTORY LEFT JOIN SENSOR ON HISTORY.sensor_id = SENSOR.id'

        conditions = []

        if start_date and end_date:
            conditions.append(f"update_time BETWEEN '{start_date}' AND '{end_date}'")
        elif start_date:
            conditions.append(f"update_time >= '{start_date}'")
        elif end_date:
            conditions.append(f"update_time <= '{end_date}'")
            
        if sensor_id is not None:
            conditions.append(f"HISTORY.sensor_id = {sensor_id}")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Exécution de la requête SQL
        cursor.execute(query)
        items = cursor.fetchall()
        # Conversion des résultats en liste de dictionnaires
        items_list = [{"sensor_id": row[1], "temperature": row[2], "humidity": row[3], "battery": row[4], "signal_rssi": row[5], "date": row[6], "sensor_name": row[7]} for row in items]

        return items_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour forcer une mise à jour immédiate
@app.get("/force-update/")
async def force_update(background_tasks: BackgroundTasks):
    """
    Force une mise à jour immédiate des données à partir du service web externe.

    Returns:
    - dict: Message indiquant que la mise à jour est en cours.
    """
    background_tasks.add_task(get_web_service)
    return {"message": "Mise à jour forcée en cours"}

@app.put("/sensor/{sensor_id}/update-name")
async def update_sensor_name(sensor_id: int = Path(..., title="ID du capteur", ge=1), new_name: str = Query(..., title="Nouveau nom du capteur")):
    """
    Met à jour le nom d'un capteur dans la base de données.

    Parameters:
    - sensor_id (int): L'ID du capteur à mettre à jour.
    - update_data (SensorUpdate): Les données de mise à jour du capteur.

    Returns:
    - dict: Message de confirmation de la mise à jour.
    """
    try:
        # Exécuter la mise à jour du nom du capteur dans la base de données
        cursor.execute("UPDATE SENSOR SET name = ? WHERE id = ?", (new_name, sensor_id))
        conn.commit()

        return {"message": f"Nom du capteur avec l'ID {sensor_id} mis à jour avec succès"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour supprimer un capteur
@app.delete("/sensor/{sensor_id}/delete")
async def delete_sensor(sensor_id: int = Path(..., title="ID du capteur", ge=1)):
    """
    Supprime un capteur de la base de données.

    Parameters:
    - sensor_id (int): L'ID du capteur à supprimer.

    Returns:
    - dict: Message de confirmation de la suppression du capteur.
    """
    try:
        # Exécuter la suppression du capteur dans la base de données
        cursor.execute("DELETE FROM SENSOR WHERE id = ?", (sensor_id,))
        conn.commit()

        return {"message": f"Capteur avec l'ID {sensor_id} supprimé avec succès"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("settings/alert/{sensor_id}")
def set_alert(name, low_humidity, high_humidity, low_temperature, high_temperature, frequence, last_send, email, user_id, sensor_id, list_alerts_id): 
    """summary :
    Réccupère les paramètres d'une alerte définies par l'utilisateur et le stock dans la BDD
    Si l'utilisateur supprime une ou des alertes, list_alerts_id = liste des id des alertes à supprimer
    """ 
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Alerts (name, low_humidity, high_humidity, low_temperature, high_temperature, frequence, last_send, email, user_id, sensor_id) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (name, low_humidity, high_humidity, low_temperature, high_temperature, frequence, last_send, email, user_id, sensor_id))

    conn.commit()
    conn.close()

    #if len(list_alerts_id) > 0:
    #    maj_alert(list_alerts_id, 'DELETE')

# Au démarrage, démarrer l'ordonnanceur
@app.on_event("startup")
def startup_event():
    scheduler.start()

# Fermeture de la connexion à la base de données lors de l'arrêt de l'application
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    conn.close()
