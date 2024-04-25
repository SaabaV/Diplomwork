import mysql.connector


class User:
    def __init__(self, user_id, username, password, saved_criteria):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.saved_criteria = saved_criteria

    @classmethod
    def from_database(cls, cursor, username):
        cursor.execute("SELECT * FROM user_criteria WHERE user_id = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return cls(*user_data)
        else:
            return None

    def save_criteria(self, cursor, criteria):
        try:
            for criteria_name, criteria_value in criteria.items():
                cursor.execute("INSERT INTO user_criteria (user_id, criteria_name, criteria_value) VALUES (%s, %s, %s)",
                               (self.user_id, criteria_name, criteria_value))
            print("Criteria saved successfully.")
        except mysql.connector.Error as e:
            print("Error saving criteria:", e)

    def load_criteria(self, cursor):
        try:
            cursor.execute("SELECT criteria_name, criteria_value FROM user_criteria WHERE user_id = %s",
                           (self.user_id,))
            criteria = {}
            for row in cursor.fetchall():
                criteria[row[0]] = row[1]
            print("Loaded user criteria:", criteria)
            return criteria
        except mysql.connector.Error as e:
            print("Error loading criteria:", e)
            return {}


