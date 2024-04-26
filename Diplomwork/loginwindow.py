#loginwindow.py
import sys
import bcrypt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
import mysql.connector
from user_module import User
from movie_window import SearchWindow
from mydatabase import DatabaseManager
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
cursor = db.cursor()


class LoginWindow(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.registration_button = QPushButton("Sign up")
        self.registration_button.clicked.connect(self.open_registration_window)
        layout.addWidget(self.registration_button)

        self.central_widget.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        cursor.execute("SELECT * FROM movies_users WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if user_data:
            hashed_password = user_data[2].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                print("Successful login.")
                db_manager = DatabaseManager(host="localhost", user="root", password="Jf223nbl1024N!vlad",
                                             database="movie")
                self.search_window = SearchWindow(user=User(*user_data), db_manager=db_manager)
                self.search_window.show()
                self.close()
                return
            else:
                print("Incorrect password.")
        else:
            print("User not found or incorrect username.")

    def open_registration_window(self):
        self.registration_window = RegistrationWindow(self)
        self.registration_window.show()
        self.hide()


class RegistrationWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Registration")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("Sign up")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.cancel_button = QPushButton("Back")
        self.cancel_button.clicked.connect(self.close_registration)
        layout.addWidget(self.cancel_button)

        self.central_widget.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        print("Attempting to register user with username:", username)
        print("Password to be hashed:", password)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                        bcrypt.gensalt()).decode()  # добавляем явное указание кодировки
        print("Hashed password:", hashed_password)

        cursor.execute("SELECT * FROM movies_users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            print("User with this username already exists.")
        else:
            cursor.execute("INSERT INTO movies_users (username, password, saved_criteria) VALUES (%s, %s, %s)",
                           (username, hashed_password, ""))
            db.commit()
            print("User successfully registered.")
            self.close()
            self.login_window.show()

    def close_registration(self):
        self.close()
        self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow(cursor)
    login_window.show()
    sys.exit(app.exec_())



