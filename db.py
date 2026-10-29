"""
db.py
Single place responsible for opening a connection to the existing
"loco_info" MySQL database. No queries that modify data live here.
"""

import mysql.connector
from mysql.connector import Error

import config


def get_connection(database=None):
    """
    Opens and returns a new MySQL connection using the settings from
    config.py (which reads from environment variables / .env).
    Supports choosing database ('loco_info' or 'hhp_loco_info').
    Includes automatic fallback between configured password and empty password
    to ensure seamless compatibility with local XAMPP/MySQL installations.
    """
    target_db = database or config.DB_NAME
    try:
        return mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=target_db,
            autocommit=True,
        )
    except mysql.connector.Error as err:
        # Error 1045 is ER_ACCESS_DENIED_ERROR
        if getattr(err, 'errno', None) == 1045:
            alt_password = "" if config.DB_PASSWORD != "" else "root"
            try:
                return mysql.connector.connect(
                    host=config.DB_HOST,
                    user=config.DB_USER,
                    password=alt_password,
                    database=target_db,
                    autocommit=True,
                )
            except Exception:
                raise err
        raise err


def get_hhp_connection():
    """Returns a connection to the HHP Loco database (hhp_loco_info)."""
    return get_connection(database=config.HHP_DB_NAME)


def list_tables():
    """
    Harmless read-only check: opens a connection and runs SHOW TABLES.
    Does not INSERT, UPDATE, or DELETE anything.
    Returns a list of table name strings.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    finally:
        conn.close()
