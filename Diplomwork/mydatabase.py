import mysql.connector
import random
import configparser
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Создание базового класса для определения моделей
Base = declarative_base()


class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    genre_search = Column(String(255))
    genre_answer = Column(String(255))
    runtime_search = Column(String(255))
    runtime_answer = Column(String(255))
    cast_search = Column(String(255))
    cast_answer = Column(String(255))
    directors_search = Column(String(255))
    directors_answer = Column(String(255))
    imdb_rating_search = Column(String(255))
    imdb_rating_answer = Column(String(255))
    year_search = Column(Integer)
    year_answer = Column(Integer)
    timestamp = Column(TIMESTAMP)

# Создание соединения с базой данных
engine = create_engine('mysql://root:Jf223nbl1024N!vlad@localhost/movie')

# Создание таблицы (если её нет)
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


def insert_search_history(user_id, genre_search, genre_answer, runtime_search, runtime_answer, cast_search, cast_answer, directors_search, directors_answer, imdb_rating_search, imdb_rating_answer, year_search, year_answer):
    new_search = SearchHistory(
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
        year_answer=year_answer,
        timestamp=datetime.now()
    )

    session.add(new_search)
    session.commit()

    session.close()


class DatabaseManager:
    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.db = None
        self.cursor = None
        self.connected = False
        self.connect()

    def connect(self):
        try:
            self.db = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.db.cursor()
            self.connected = True
            print("Connected to the database")
        except mysql.connector.Error as e:
            print("Error connecting to the database:", e)
            raise

    def disconnect(self):
        if self.db:
            self.db.close()
            print("Disconnected from the database")
            self.connected = False

    def get_recommendations(self, criteria, limit=12):
        try:
            if not self.cursor:
                raise ValueError("Database connection is not established")

            sql = "SELECT * FROM movies WHERE "
            conditions = []
            values = []

            if criteria["genres"]:
                conditions.append("FIND_IN_SET(%s, genres) > 0")
                values.append(criteria["genres"])

            if criteria["runtime"] and criteria["runtime"].isdigit():
                conditions.append("runtime <= %s")
                values.append(int(criteria["runtime"]))

            if criteria["cast"]:
                conditions.append("cast LIKE %s")
                values.append('%' + criteria["cast"] + '%')

            if criteria["languages"]:
                languages = criteria["languages"].strip()
                conditions.append("languages LIKE %s")
                values.append('%' + languages + '%')

            if criteria["directors"]:
                conditions.append("directors LIKE %s")
                values.append('%' + criteria["directors"] + '%')

            if criteria["year"]:
                conditions.append("year = %s")
                values.append(criteria["year"])

            if criteria["imdb_rating_combo"]:
                conditions.append("`imdb.rating` >= %s")
                values.append(criteria["imdb_rating_combo"])

            if conditions:
                sql += " AND ".join(conditions)
                count_query = f"SELECT COUNT(*) FROM movies WHERE {' AND '.join(conditions)}"
                self.cursor.execute(count_query, values)
                total_count = self.cursor.fetchone()[0]
                if total_count > limit:
                    sql += " ORDER BY RAND()"
                    sql += " LIMIT %s"
                    values.append(limit)
                else:
                    sql += " LIMIT %s"
                    values.append(total_count)
                print("SQL query:", sql)
                self.cursor.execute(sql, values)
                movies = self.cursor.fetchall()
                print("Retrieved movies from the database:")
                for movie in movies:
                    print(movie)
                return movies
            else:
                print("No search criteria has been selected.")
                return []

        except mysql.connector.Error as e:
            print("An error occurred while executing a database query:", e)
            return []

    def get_cast(self):
        try:
            self.cursor.execute("""
                SELECT DISTINCT JSON_UNQUOTE(JSON_EXTRACT(cast, '$[*]')) as actor
                FROM movies
                CROSS JOIN JSON_TABLE(cast, "$[*]" COLUMNS(actor VARCHAR(255) PATH "$")) as actors
                ORDER BY actor;
            """)
            cast = self.cursor.fetchall()
            return [actor[0] for actor in cast]
        except Exception as e:
            print("An error occurred while fetching cast members:", e)
            return []

    def get_directors(self):
        try:
            self.cursor.execute("SELECT DISTINCT directors FROM movies")
            directors_data = self.cursor.fetchall()
            directors_list = []
            for directors in directors_data:
                directors = directors[0].strip()
                directors = directors.strip('[]')
                directors_list.extend(directors.split(', '))
            # Обработка строк для режиссеров
            directors_list = [director.strip() for director in directors_list]
            return directors_list
        except mysql.connector.Error as e:
            print("An error occurred while fetching directors:", e)
            return []

    def get_imdb_ratings(self):
        try:
            self.cursor.execute("""
                SELECT DISTINCT `imdb.rating`
                FROM movies
                ORDER BY `imdb.rating`;
            """)
            ratings = self.cursor.fetchall()
            return [rating[0] for rating in ratings]
        except mysql.connector.Error as e:
            print("An error occurred while fetching IMDb ratings:", e)
            return []

    def get_genres(self):
        try:
            if not self.connected:
                raise ValueError("Database connection is not established")

            self.cursor.execute("""
                SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(genres, ',', numbers.n), ',', -1) as genre
                FROM movies
                INNER JOIN (
                    SELECT (a.N + b.N * 10 + 1) n
                    FROM (SELECT 0 as N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
                    CROSS JOIN (SELECT 0 as N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
                    ORDER BY n
                ) numbers ON CHAR_LENGTH(genres) - CHAR_LENGTH(REPLACE(genres, ',', '')) >= numbers.n - 1
                ORDER BY genre;
            """)
            genres = self.cursor.fetchall()
            return [genre[0] for genre in genres]
        except Exception as e:
            print("An error occurred while fetching genres:", e)
            return []

    def get_languages(self):
        try:
            if not self.connected:
                raise ValueError("Database connection is not established")

            self.cursor.execute("""
                SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(REPLACE(REPLACE(languages, '"', ''), ']', ''), ',', numbers.n), ',', -1) as language
                FROM movies
                INNER JOIN (
                    SELECT (a.N + b.N * 10 + 1) n
                    FROM (SELECT 0 as N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
                    CROSS JOIN (SELECT 0 as N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
                    ORDER BY n
                ) numbers ON CHAR_LENGTH(REPLACE(REPLACE(languages, '"', ''), ']', '')) - CHAR_LENGTH(REPLACE(REPLACE(REPLACE(languages, '"', ''), ']', ''), ',', '')) >= numbers.n - 1
                ORDER BY language;
            """)
            languages = self.cursor.fetchall()
            return [language[0] for language in languages]
        except mysql.connector.Error as e:
            print("An error occurred while fetching languages:", e)
            return []

    def get_years(self):
        try:
            self.cursor.execute("SELECT DISTINCT year FROM movies ORDER BY year")
            years = self.cursor.fetchall()
            return [str(year[0]) for year in years]
        except mysql.connector.Error as e:
            print("An error occurred while fetching years:", e)
            return []


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_manager = DatabaseManager(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
    db_manager.connect()
    directors = db_manager.get_directors()
    print("Directors:", directors)
    imdb_ratings = db_manager.get_imdb_ratings()
    print("IMDb Ratings:", imdb_ratings)
    genres = db_manager.get_genres()
    print("Genres:", genres)
    years = db_manager.get_years()
    print("Years:", years)
    languages = db_manager.get_languages()
    print("Languages:", languages)
    db_manager.disconnect()


