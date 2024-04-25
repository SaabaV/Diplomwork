from PyQt5.QtWidgets import QMenu, QGroupBox, QApplication, QDialog, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from io import BytesIO
import requests


class MovieWidget(QWidget):
    def __init__(self, movie):
        super().__init__()

        # Основной макет
        main_layout = QHBoxLayout()

        # Макет с информацией о фильме
        movie_info_layout = QVBoxLayout()

        # Название фильма
        self.title_label = QLabel("<b>Movie:</b> " + str(movie[6]))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16pt")
        self.title_label.setFixedHeight(50)
        movie_info_layout.addWidget(self.title_label)

        # Добавляем остальные атрибуты фильма
        attributes = [
            ("<b>Genre:</b>", ", ".join(str(movie[2]).strip("{}'").replace("'", "").split(', '))),
            ("<b>Runtime:</b>", str(movie[3]) + " min"),
            ("<b>Cast:</b>", ", ".join(str(movie[4]).strip("[]'").replace("'", "").replace('"', '').split(', '))),
            ("<b>Director(s):</b>", ", ".join(str(movie[8]).strip("[]'").replace("'", "").replace('"', '').split(', '))),
            ("<b>Year:</b>", str(movie[10])),
            ("<b>IMDb Rating:</b>", str(movie[11]))
        ]

        for attr_text, value in attributes:
            attr_label = QLabel("{} {}".format(attr_text, value))
            attr_label.setWordWrap(False)
            attr_label.setMaximumWidth(700)
            movie_info_layout.addWidget(attr_label, alignment=Qt.AlignLeft)

        # Добавляем макет с информацией о фильме в основной макет
        main_layout.addLayout(movie_info_layout)

        # Добавляем макет с описанием фильма слева от изображения
        plot_layout = QVBoxLayout()

        # Создаем виджет прокрутки для описания фильма
        plot_scroll_area = QScrollArea()
        plot_scroll_area.setWidgetResizable(True)
        plot_scroll_area.setFixedWidth(300)
        plot_scroll_area.setMinimumHeight(100)

        # Отформатированное описание фильма
        plot_label = QLabel("<b>Plot:</b> " + str(movie[1]))
        plot_label.setWordWrap(True)
        plot_scroll_area.setWidget(plot_label)

        plot_layout.addWidget(plot_scroll_area)

        #добавляем блок с описанием
        main_layout.addLayout(plot_layout)

        # Макет с изображением
        poster_layout = QVBoxLayout()
        poster_layout.setAlignment(Qt.AlignTop)  #выравнивание

        try:
            poster_url = movie[5]
            response = requests.get(poster_url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                if not pixmap.isNull():
                    poster_label = QLabel()
                    poster_label.setPixmap(pixmap.scaledToWidth(200))
                    poster_layout.addWidget(poster_label, alignment=Qt.AlignCenter)
                else:
                    print("Failed to load the image from URL:", poster_url)
            else:
                print("Failed to fetch image from URL:", poster_url)
        except Exception as e:
            print("Error loading poster:", e)

        # Добавляем макет с изображением в основной макет
        main_layout.addLayout(poster_layout)

        self.setLayout(main_layout)

        self.setStyleSheet(
            """
            MovieWidget:hover {
                background-color: #4B4D4D;
            }
            """
        )


class ResultsWindow(QMainWindow):
    def __init__(self, movies_list):
        super().__init__()
        self.setWindowTitle("Movie Recommendations")
        self.setGeometry(800, 800, 1100, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)  # Добавляем отступы
        self.central_widget.setStyleSheet("background-color: #F1F1F1;")  # Изменяем цвет фона

        # Заголовок окна
        title_label = QLabel("<h1 style='color: #1D616D; text-align: center;'> Recommended Movies </h1>")
        layout.addWidget(title_label)

        # Разделительная линия
        line_label = QLabel()
        line_label.setFixedHeight(2)
        line_label.setStyleSheet("background-color: #577979;")
        layout.addWidget(line_label)

        self.movies_list = QListWidget()
        self.movies_list.setStyleSheet("QListWidget:item:selected { background-color: #3a3a3a; color: grey; }")
        layout.addWidget(self.movies_list)

        for movie in movies_list:
            self.add_movie_to_interface(movie)

        # Кнопка закрытия окна
        close_button = QPushButton("Close")
        close_button.setStyleSheet(
            "QPushButton { background-color: #cc3333; color: white; border: none; padding: 8px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #bb0000; }"
        )
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        self.central_widget.setLayout(layout)

    def add_movie_to_interface(self, movie):
        movie_widget = MovieWidget(movie)
        item = QListWidgetItem()
        item.setSizeHint(movie_widget.sizeHint())
        self.movies_list.addItem(item)
        self.movies_list.setItemWidget(item, movie_widget)


class RecommendationsWindow(QDialog):
    def __init__(self, movies):
        super().__init__()
        self.setWindowTitle("Recommendations")
        self.setGeometry(1260, 1260, 800, 800)

        layout = QVBoxLayout()

        for movie in movies[:8]:
            movie_plot = movie[1]
            genres = ', '.join(movie[2])
            runtime = str(movie[3]) + " minutes"
            cast = ', '.join(movie[4])
            title = movie[6]
            movie_poster_url = movie[5]
            rating = str(movie[11])
            director = ', '.join(movie[8])
            year = str(movie[10])

            group_box = QGroupBox(f"{title}")
            group_layout = QVBoxLayout()

            plot_label = QLabel(f"Plot: {movie_plot}")
            plot_label.setWordWrap(True)
            plot_label.setMaximumHeight(100)
            group_layout.addWidget(plot_label)

            genres_label = QLabel(f"Genres: {genres}")
            genres_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(genres_label)

            runtime_label = QLabel(f"Runtime: {runtime}")
            runtime_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(runtime_label)

            cast_label = QLabel(f"Cast: {cast}")
            cast_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(cast_label)

            rating_label = QLabel(f"IMDb Rating: {rating}")
            rating_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(rating_label)

            director_label = QLabel(f"Director(s): {director}")
            director_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(director_label)

            year_label = QLabel(f"Year: {year}")
            year_label.setMaximumHeight(100)  # Устанавливаем максимальную высоту
            group_layout.addWidget(year_label)

            # Добавление постера фильма
            try:
                pixmap = QPixmap(movie_poster_url)
                poster_label = QLabel()
                poster_label.setPixmap(pixmap)
                group_layout.addWidget(poster_label)
            except Exception as e:
                print("Error loading poster:", e)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

            # Применяем стили для подсветки блока при наведении
            group_box.setStyleSheet(
                "QGroupBox:hover { border: 2px solid #59827D; border-radius: 5px; }"
            )

            # Добавляем возможность копирования текста при щелчке правой кнопкой мыши
            group_box.setContextMenuPolicy(Qt.CustomContextMenu)
            group_box.customContextMenuRequested.connect(self.show_context_menu)

        self.setLayout(layout)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        action_copy = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == action_copy:
            widget = self.sender()
            clipboard = QApplication.clipboard()
            title = widget.title()
            clipboard.setText(title)
















