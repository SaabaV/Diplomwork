import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import logging
from recomend_movie import ResultsWindow
from user_module import User
from mydatabase import DatabaseManager
import configparser
from mydatabase import insert_search_history

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

            # Добавим выводы здесь
            genres = type(criteria["genres"])
            runtime = type(criteria["runtime"])
            imdb_rating = type(criteria["imdb_rating_combo"])
            limit = 12

            logging.info("Genres value: %s", type(genres))
            logging.info("Runtime value: %s", type(runtime))
            logging.info("IMDb rating value: %s", type(imdb_rating))
            logging.info("Limit value: %s", type(limit))
            logging.info("Selected genre: %s", type(self.genre_combo.currentText()))
            logging.info("Search Criteria: %s", type(criteria))

            movies = self.db_manager.get_recommendations(criteria)
            logging.info("Found movies: %s", movies)
            if movies:
                self.show_recommendations(movies)
                self.save_criteria(criteria, movies)
            else:
                logging.info("No recommendations")
        except Exception as e:
            logging.error("Error searching for movies: %s", e)

    def show_recommendations(self, movies):
        self.results_window = ResultsWindow(movies)
        self.results_window.show()

    def save_criteria(self, criteria, movies):
        if self.user:
            try:
                user_id = self.user.user_id
                if not isinstance(user_id, str):
                    user_id = str(user_id)
                user_id = str(user_id)
                # Извлекаем значения критериев поиска из словаря criteria
                genre_search = criteria.get("genres", "")
                runtime_search = criteria.get("runtime", "")
                cast_search = criteria.get("cast", "")
                directors_search = criteria.get("directors", "")
                imdb_rating_search = criteria.get("imdb_rating_combo", "")
                year_search = str(criteria.get("year", None))

                if movies and len(movies) > 0:
                    first_movie = movies[0]
                    if len(first_movie) > 14:
                        genre_answer = ', '.join(first_movie[4]) if isinstance(first_movie[4], (list, tuple)) else str(
                            first_movie[4])
                        runtime_answer = str(first_movie[6])
                        cast_answer = ', '.join(first_movie[8]) if isinstance(first_movie[8], (list, tuple)) else str(
                            first_movie[8])
                        directors_answer = ', '.join(first_movie[10]) if isinstance(first_movie[10],
                                                                                    (list, tuple)) else str(
                            first_movie[10])
                        imdb_rating_answer = ', '.join(str(first_movie[12])) if isinstance(first_movie[12],
                                                                                           (list, tuple)) else str(
                            first_movie[12])
                        year_answer = str(first_movie[14]) if first_movie[14] is not None else None
                    else:
                        logging.warning("First movie does not contain all required information.")
                        genre_answer = ""
                        runtime_answer = ""
                        cast_answer = ""
                        directors_answer = ""
                        imdb_rating_answer = ""
                        year_answer = None

                else:
                    logging.warning("No movies found.")
                    genre_answer = ""
                    runtime_answer = ""
                    cast_answer = ""
                    directors_answer = ""
                    imdb_rating_answer = ""
                    year_answer = ""

                # Преобразуем пустые строки в значения None
                if not year_search:
                    year_search = None

                insert_search_history(
                    user_id=user_id,
                    genre_search=genre_search,
                    genre_answer=genre_answer,
                    runtime_search=runtime_search,
                    runtime_answer=runtime_answer,
                    cast_search=cast_search,
                    cast_answer=cast_answer,
                    directors_search=directors_search,
                    directors_answer=directors_answer,
                    imdb_rating_search=imdb_rating_search,
                    imdb_rating_answer=imdb_rating_answer,
                    year_search=year_search,
                    year_answer=year_answer
                )

                logging.info("User criteria saved successfully.")
            except Exception as e:
                logging.error("Error saving user criteria: %s", e)
        else:
            logging.warning("No user to save criteria for.")


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

