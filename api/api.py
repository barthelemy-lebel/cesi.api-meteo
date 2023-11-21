import json
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


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


def save_to_json(data_list: List[dict], filename: str = "data.json") -> None:
    """
    Sauvegarde une liste de données au format JSON dans un fichier.

    Parameters:
    - data_list (List[dict]): La liste de données à sauvegarder.
    - filename (str): Le nom du fichier de sauvegarde JSON.
    """
    with open(filename, "w") as json_file:
        json.dump(data_list, json_file, indent=2)


def get_web_service(limit: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
    """
    Récupère les données du service web externe, les transforme et les sauvegarde localement.

    Parameters:
    - limit (int): Le nombre maximal d'éléments à récupérer.
    - start_date (Optional[str]): La date de début pour filtrer les données (format ISO).
    - end_date (Optional[str]): La date de fin pour filtrer les données (format ISO).

    Returns:
    - List[dict]: La liste des données transformées.
    """
    url = f"http://app.objco.com:8099/?account=MRHAOCUYL2&limit={limit}"

    # Ajout des paramètres start_date et end_date à l'URL
    if start_date:
        url += f"&start_date={start_date}"
    if end_date:
        url += f"&end_date={end_date}"

    datas = requests.get(url)
    datas.encoding
    datas = datas.text
    datas = json.loads(datas)

    # Transformation de chaque élément des datas
    result = []
    for data in datas:
        exa_code = data[1]

        date = data[2]
        date = convert_date(date)

        # Filtrage par date
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue

        tag_info_index = exa_code.index("62182")
        tag_info = exa_code[tag_info_index:tag_info_index+22]

        id_capteur = tag_info[0:7]

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

        # Récupérer les données
        saved_data = {
            "id_capteur": id_capteur,
            "name": name,
            "sensor_type": sensor_type,
            "temperature": temperature,
            "humidity": humidity,
            "date": date,
            "rssi_signal": rssi_signal
        }
        result.append(saved_data)

    # Sauvegarder les données dans un fichier JSON
    existing_data = load_existing_data()
    existing_data += result
    save_to_json(existing_data)

    return result


def load_existing_data(filename: str = "data.json") -> List[dict]:
    """
    Charge les données sauvegardées localement à partir d'un fichier JSON.

    Parameters:
    - filename (str): Le nom du fichier de sauvegarde JSON.

    Returns:
    - List[dict]: La liste des données sauvegardées.
    """
    try:
        with open(filename, "r") as json_file:
            existing_data = json.load(json_file)
        if not isinstance(existing_data, list):
            existing_data = []
        return existing_data
    except FileNotFoundError:
        return []


@app.get("/", response_model=List[dict], summary="Récupérer les données du service web externe")
async def read_root(limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Récupère les données du service web externe, les transforme et les sauvegarde localement.

    Parameters:
    - limit (int): Le nombre maximal d'éléments à récupérer.
    - start_date (Optional[str]): La date de début pour filtrer les données (format ISO).
    - end_date (Optional[str]): La date de fin pour filtrer les données (format ISO).

    Returns:
    - List[dict]: La liste des données transformées.
    """
    return get_web_service(limit, start_date=start_date, end_date=end_date)


@app.get("/get_saved_data", response_model=List[dict], summary="Récupérer les données sauvegardées localement")
async def get_saved_data():
    """
    Récupère les données sauvegardées localement.

    Returns:
    - List[dict]: La liste des données sauvegardées.
    """
    existing_data = load_existing_data()
    if existing_data:
        return JSONResponse(content=existing_data)
    else:
        raise HTTPException(
            status_code=404, detail="Aucune donnée n'a été enregistrée.")


@app.delete("/delete_data/{id_capteur}", response_model=dict, summary="Supprimer les données d'un capteur")
async def delete_data(id_capteur: str):
    """
    Supprime les données associées à un capteur.

    Parameters:
    - id_capteur (str): L'identifiant du capteur dont les données doivent être supprimées.

    Returns:
    - dict: Un message indiquant si la suppression a réussi.
    """
    existing_data = load_existing_data()

    # Filtrer les données pour exclure celles associées à l'id_capteur
    filtered_data = [
        data for data in existing_data if data["id_capteur"] != id_capteur]

    # Vérifier si des données ont été effectivement supprimées
    if len(filtered_data) == len(existing_data):
        raise HTTPException(
            status_code=404, detail=f"Aucune donnée associée à l'id_capteur {id_capteur} n'a été trouvée.")

    # Sauvegarder les données filtrées
    save_to_json(filtered_data)

    return {"message": f"Données associées à l'id_capteur {id_capteur} supprimées avec succès."}
