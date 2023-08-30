import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB"),
        )
        self.cursor = self.connection.cursor()

    def add_item(self, query, data):
        self.cursor.execute(query, data)
        _id = self.cursor.lastrowid
        self.connection.commit()
        return _id

    def add_items(self, query, data):
        self.cursor.executemany(query, data)
        _id = self.cursor.lastrowid
        self.connection.commit()
        return _id

    def get_item(self, query, data=None):
        self.cursor.execute(query, data)
        response = self.cursor.fetchone()
        return response

    def get_items(self, query, data=None):
        self.cursor.execute(query, data)
        response = self.cursor.fetchall()
        return response

    def update_item(self, query, data):
        self.cursor.execute(query, data)
        _id = self.cursor.lastrowid
        self.connection.commit()
        return _id