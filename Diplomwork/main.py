import sys
from PyQt5.QtWidgets import QApplication
from loginwindow import LoginWindow
from mydatabase import DatabaseManager
import configparser


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_manager = DatabaseManager(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
    db_manager.connect()

    app = QApplication(sys.argv)
    login_window = LoginWindow(db_manager)
    login_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



