import mysql.connector
import logging


class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

    @classmethod
    def from_database(cls, cursor, username):
        cursor.execute("SELECT * FROM movies_users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return cls(*user_data)
        else:
            return None

    def load_criteria(self, cursor):
        try:
            cursor.execute("SELECT * FROM search_history WHERE user_id = %s", (self.user_id,))
            criteria = {}
            for row in cursor.fetchall():
                criteria["genres"] = row[2]
                criteria["runtime"] = row[4]
                criteria["cast"] = row[6]
                criteria["directors"] = row[8]
                criteria["imdb_rating_combo"] = row[10]
                criteria["year"] = row[12]
            print("Loaded user criteria:", criteria)
            return criteria
        except mysql.connector.Error as e:
            print("Error loading criteria:", e)
            return {}


