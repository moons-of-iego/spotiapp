import logging
import mysql.connector
import spotiapp.config as config
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__file__)


def test_db_connection():
    logger.info(f"Tentative de connexion à {config.HOST}...")
    connexion = mysql.connector.connect(
        host=config.HOST,
        port=config.PORT,
        user=config.USER_LOGIN,
        password=config.USER_PASSWORD,
        database=config.NAME_DB,
    )

    assert connexion.is_connected(), "Erreur de connexion"
    if connexion.is_connected():
        logger.info("Connecté au container")
        cursor = connexion.cursor()
        cursor.execute("SHOW DATABASES;")
        res = cursor.fetchall()
        logger.info(f"Liste des bases de données: {res}")

    if "connexion" in locals() and connexion.is_connected():
        cursor.close()
        connexion.close()
        logger.info("Connexion fermée proprement")
