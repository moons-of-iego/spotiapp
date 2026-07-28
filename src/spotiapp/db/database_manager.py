import logging
import pandas as pd
from mysql.connector.pooling import MySQLConnectionPool
import spotiapp.config as config

logger = logging.getLogger(__name__)


class DatabaseManager:
    _pool: MySQLConnectionPool = None

    @classmethod
    def initialize(cls, pool_size: int = 5):

        if cls._pool is None:
            try:
                cls._pool = MySQLConnectionPool(
                    pool_name="spotiapp_pool",
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=config.HOST,
                    port=int(config.PORT),
                    database=config.NAME_DB,
                    user=config.USER_LOGIN,
                    password=config.USER_PASSWORD,
                )
                logger.info("MySQL connection pool initialized.")
            except Exception as e:
                logger.error(e)
                raise e

    @classmethod
    def execute_transaction(
        cls, query: str, params: tuple = None, verbose: bool = False
    ) -> pd.DataFrame:
        """
        Execute a transaction on the database.

        :param str query: the query to execute.
        :param tuple params: (Optional) The parameters of the query
        :param bool verbose: True to return the data fetched by the query. Defaults to None.

        :return data (pd.DataFrame): the data fetched from the query.
        """
        if cls._pool is None:
            logger.error("Pool not initialized.")
            cls.initialize()

        connection = None
        cursor = None
        success = False
        data: pd.DataFrame = None

        try:
            connection = cls._pool.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, params)
            connection.commit()
            success = True

            if verbose:
                data = cursor.fetchall()
                print(data)

        except Exception as e:
            logger.error(e)
            raise e

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return data

    @classmethod
    def executescript_transaction(cls, script_query: str):
        if cls._pool is None:
            logger.error("Pool not initialized.")
            cls.initialize()

        connection = None
        cursor = None
        success = False

        try:
            connection = cls._pool.get_connection()
            cursor = connection.cursor()

            results = cursor.execute(script_query, multi=True)

            for _ in results:
                pass

            connection.commit()
            logger.info("Script succeeded")
            success = True

        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Erreur lors de l'exécution du script SQL : {e}")
            raise e

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return success

    @classmethod
    def executemany_transactions(cls, query: str, seq_of_params: list[tuple[str, ...]]):
        if cls._pool is None:
            logger.error("Pool not initialized.")
            cls.initialize()

        connection = None
        cursor = None
        success = False

        try:
            connection = cls._pool.get_connection()
            cursor = connection.cursor()

            cursor.executemany(query, seq_of_params)
            connection.commit()
            success = True

        except Exception as e:
            logger.error(e)
            raise e

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return success
