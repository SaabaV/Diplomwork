import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import logging
from recomend_movie import ResultsWindow
from user_module import User
from mydatabase import DatabaseManager
import configparser

logging.basicConfig(level=logging.DEBUG, filename='search_window.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class SearchWindow(QMainWindow):
    def __init__(self, user, db_manager):
        super().__init__()
        self.results_window = None
        self.db_manager = db_manager
        self.user = user
        self.cursor = self.db_manager.cursor

        self.setWindowTitle("Movie Search")
        self.setGeometry(100, 100, 400, 300)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.genre_label = QLabel("Genre:")
        layout.addWidget(self.genre_label)
        self.genre_combo = QComboBox()
        self.genre_combo.addItems([""] + self.db_manager.get_genres())
        layout.addWidget(self.genre_combo)

        self.runtime_label = QLabel("Duration (min):")
        layout.addWidget(self.runtime_label)
        self.runtime_input = QLineEdit()
        layout.addWidget(self.runtime_input)

        self.cast_label = QLabel("Cast:")
        layout.addWidget(self.cast_label)
        self.cast_combo = QComboBox()
        self.cast_combo.addItems([""] + self.db_manager.get_cast())
        layout.addWidget(self.cast_combo)

        self.languages_label = QLabel("Languages:")
        layout.addWidget(self.languages_label)
        self.languages_combo = QComboBox()
        self.languages_combo.addItems([""] + self.db_manager.get_languages())
        layout.addWidget(self.languages_combo)

        self.directors_label = QLabel("Director:")
        layout.addWidget(self.directors_label)
        self.directors_combo = QComboBox()
        self.directors_combo.setMaximumWidth(200)
        self.directors_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.directors_combo.addItems([""] + self.db_manager.get_directors())
        layout.addWidget(self.directors_combo)
        self.directors_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.custom_director_label = QLabel("Custom Director:")
        layout.addWidget(self.custom_director_label)
        self.custom_director_input = QLineEdit()
        layout.addWidget(self.custom_director_input)

        self.year_label = QLabel("Year:")
        layout.addWidget(self.year_label)
        self.year_combo = QComboBox()
        self.year_combo.addItems([""] + self.db_manager.get_years())
        layout.addWidget(self.year_combo)
        self.year_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.imdb_rating_label = QLabel("IMDb Rating:")
        layout.addWidget(self.imdb_rating_label)
        self.imdb_rating_combo = QComboBox()
        ratings = self.db_manager.get_imdb_ratings()
        self.imdb_rating_combo.addItems([""] + [str(rating) for rating in ratings])
        layout.addWidget(self.imdb_rating_combo)

        self.search_button = QPushButton("Searching")
        self.search_button.clicked.connect(self.search_movies)
        layout.addWidget(self.search_button)
        self.central_widget.setLayout(layout)

    def search_movies(self):
        try:
            criteria = {
                "genres": self.genre_combo.currentText(),
                "runtime": (self.runtime_input.text()),
                "cast": self.cast_combo.currentText(),
                "languages": self.languages_combo.currentText(),
                "directors": self.directors_combo.currentText(),
                "custom_director": self.custom_director_input.text(),
                "year": self.year_combo.currentText(),
                "imdb_rating_combo": self.imdb_rating_combo.currentText()
            }

            if criteria["custom_director"]:
                criteria["directors"] = criteria["custom_director"]

            logging.info("Selected genre: %s", self.genre_combo.currentText())
            logging.info("Search Criteria: %s", criteria)
            movies = self.db_manager.get_recommendations(criteria)
            logging.info("Found movies: %s", movies)
            if movies:
                self.show_recommendations(movies)
                self.save_criteria(criteria)  # Обновленный вызов метода save_criteria
            else:
                logging.info("No recommendations")
        except Exception as e:
            logging.error("Error searching for movies: %s", e)

    def save_criteria(self, criteria):
        if self.user:
            try:
                criteria_name = criteria.get("criteria_name", "")
                criteria_value = criteria.get("criteria_value", "")
                cursor = self.db_manager.cursor
                user_id = self.user.user_id  # Получаем имя пользователя
                cursor.execute("INSERT INTO user_criteria (user_id, criteria_name, criteria_value) VALUES (%s, '%s', '%s')", (user_id, criteria_name, criteria_value))
                logging.info("User criteria saved successfully.")
            except Exception as e:
                logging.error("Error saving user criteria: %s", e)
        else:
            logging.warning("No user to save criteria for.")

    def show_recommendations(self, movies):
        self.results_window = ResultsWindow(movies)
        self.results_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    config = configparser.ConfigParser()
    config.read('config.ini')

    db_manager = DatabaseManager(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
    db_manager.connect()
    cursor = db_manager.cursor
    user = User.from_database(cursor, "vladislav")
    window = SearchWindow(user, db_manager)
    window.show()
    sys.exit(app.exec_())

