import os
import mysql.connector
import src.spotiapp.config as config
from dotenv import load_dotenv

load_dotenv()

try:
    print(f"Tentative de connexion à {config.HOST}...")
    connexion = mysql.connector.connect(
        host=config.HOST,
        port=config.PORT,
        user=config.USER_LOGIN,
        password=config.USER_PASSWORD,
        database=config.NAME_DB,
    )

    if connexion.is_connected():
        print("Connecté au container")
        cursor = connexion.cursor()
        cursor.execute("SHOW DATABASES;")
        res = cursor.fetchall()
        print(f"Liste des bases de données: {res}")

except mysql.connector.Error as e:
    print(f"Erreur de connexion: {e}")

finally:
    if "connexion" in locals() and connexion.is_connected():
        cursor.close()
        connexion.close()
        print("Connexion fermée proprement")
