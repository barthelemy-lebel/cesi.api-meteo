import datetime as dt
import json
import sqlite3
from typing import List


class Alert():
    def __init__(self, id, name, low_humidity=None, high_humidity=None, low_temperature=None, high_temperature=None, frequence=30, last_send=None, email=None, user_id=None, sensor_id=None):
        self.id = id
        self.name = name
        self.low_humidity = low_humidity
        self.high_humidity = high_humidity
        self.low_temperature = low_temperature
        self.high_temperature = high_temperature
        self.frequence = frequence
        self.last_send = last_send
        self.email = email
        self.user_id = user_id
        self.sensor_id = sensor_id


def create_table_alert():   
    """_summary :
    Crée la table alerte si elle n'est pas encore créée
    """           
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()

    table_alerts = '''
    CREATE TABLE IF NOT EXISTS Alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        low_humidity REAL NOT NULL,
        high_humidity REAL NOT NULL,
        low_temperature REAL NOT NULL,
        high_temperature REAL NOT NULL,
        frequence INTEGER,
        last_send DATETIME,
        email TEXT NOT NULL,
        user_id INTEGER,
        sensor_id INTEGER,
        FOREIGN KEY(sensor_id) REFERENCES Sensor(id),
        FOREIGN KEY(user_id) REFERENCES User(id)
        
    );
    '''
    cursor.execute(table_alerts)
    conn.commit()
    conn.close()


def get_alert() -> List:
    """_summary :
     Transforme les alertes de la BDD en objet et return une liste de ces objets
    """
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Alerts')
    datas = cursor.fetchall()
    conn.close()

    nb_alert = int(len(datas)/11)

    list_alerts = []
    for i in range(nb_alert):
        list_alerts.append(Alert(datas[0], datas[1], datas[2], datas[3], datas[4], datas[5], datas[6], datas[7], datas[8], datas[9], datas[10]))
        if len(datas) > 11:
            datas.pop[0:10]

    return list_alerts


def maj_alert(list_alerts, do):
    """_summary :
    Met à jour les alertes en fonctions du besoin (UPDATE, DELETE)
    Args:
        list_alerts (List): soit une liste d'alerte en objet, soit une liste d'id pour la suppression d'alertes
        do (str): indique l'action à faire (Update ou Delete)
    """
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()

    #list_alert = liste d'objets alertes à mettre à jour
    if do == 'UPDATE':
        for alert in list_alerts:
            maj = f'''
            UPDATE Alerts
            SET last_send = {alert.last_send}
            WHERE id = {alert.id}            
            );
            '''
            cursor.execute(maj)
    else: #list_alert = liste d'id d'alerte à supprimer
        for alert in list_alerts:
            maj = f'''
            DELETE Alerts
            WHERE id = {alert}            
            );
            '''
            cursor.execute(maj)
    conn.commit()
    conn.close()


def send_mail(name, message, email):
    """_summary :
        Envoi un mail en fonction de l'alerte décmenchée
    Args:
        name (str): nom de l'alerte concernée
        message (str): message texte en fonction de l'alerte qui a été déclenché
        email (str): adresses email du ou des personnes souhaitant être alertées
    """
    pass    


def is_alert(humidity, temperature):
    """summary :
    Vérifie si une des alertes doit se déclencher ou non. Si oui appelle send_mail(). Met ensuite à jour la BDD
    Args :
        humidity (float): Humidité actuelle relevée par la ou les sondes en question
        temperature (float): Température actuelle relevée par la ou les sondes en question
    """
    list_alerts = get_alert()
    for alert in list_alerts:
        #valeur de comparaison si besoin de mise à jour
        last_send = alert.last_send
        if (alert.last_send - dt.now()).total_seconds() > alert.frequence*60 or alert.last_send == '' : #transforme fréquence (minute) en seconde pour pouvoir comparer
            if alert.low_humidity != "" and alert.high_humidity != "":
                if not alert.low_humidity < humidity < alert.high_humidity :
                    message = f"Attention : le capteur {alert.sensor_id} indique que le taux d'humidité est à {humidity}, alors qu'il devrait être entre {alert.low_humidity} et {alert.high_humidity}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)
            elif alert.low_humidity != "" and alert.high_humidity == "":
                if humidity < alert.low_humidity :
                    message = f"Attention : le capteur {alert.sensor_id} indique que le taux d'humidité est à {humidity} ce qui est inférieure à votre minimum de {alert.low_humidity}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)

            else:
                if alert.high_humidity < humidity :
                    message = f"Attention : le capteur {alert.sensor_id} indique que le taux d'humidité est à {humidity} ce qui est supérieur à votre maximum de {alert.high_humidity}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)
            if alert.low_temperature != "" and alert.high_temperature != "":
                if not alert.low_temperature < temperature < alert.high_temperature :
                    message = f"Attention : le capteur {alert.sensor_id} indique que la température est à {temperature}, alors qu'elle devrait être entre {alert.low_temperature} et {alert.high_temperature}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)

            elif alert.low_temperature != "" and alert.high_temperature == "":
                if temperature < alert.low_temperature :
                    message = f"Attention : le capteur {alert.sensor_id} indique que la température est à {temperature} ce qui inférieure à votre minimum de {alert.low_temperature}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)

            else:
                if alert.high_temperature < temperature :
                    message = f"Attention : le capteur {alert.sensor_id} indique que la température est à {temperature} ce qui est supérieur à votre maximum de {alert.high_temperature}."
                    alert.last_send = dt.now()
                    send_mail(alert.name, message, alert.email)
    if last_send != alert.last_send:
        maj_alert(list_alerts, 'UPDATE') 
