The project is a movie search and recommendation application developed in Python using the PyQt5 library for creating the graphical user interface (GUI) and mysql.connector for interacting with the MySQL database. The main goal of the application is to facilitate the process of searching for movies based on specified criteria and to offer personalized recommendations to the user.

Key Components:

LoginWindow:
Provides users with the ability to log in to the system using their credentials (username and password) or to register in the system.
Login and registration are implemented through interaction with the MySQL database.
Passwords are hashed using the bcrypt library.
RegistrationWindow:
Allows new users to register by providing a unique username and password.
Checks the uniqueness of the username before registration.
Implements password hashing before saving it to the database.
DatabaseManager:
Establishes a connection to the MySQL database.
Implements methods for executing database queries, such as searching for movies based on various criteria and retrieving lists of actors, directors, genres, IMDb ratings, etc.
Handles data processing and representation for use in other parts of the application.
Provides exception handling for possible errors that may occur during database interactions.
Offers methods for retrieving various data from the database.
SearchWindow:
Provides users with an interface to specify search criteria for movies, such as genre, duration, actors, directors, IMDb rating, etc.
Allows users to view search results and receive personalized recommendations based on the entered criteria.
Provides the ability to save search results for later use and analysis.
Core Features:

Searching for movies based on various criteria: genre, duration, actors, directors, release year, IMDb rating, and more.
Registration of new users and authentication of existing ones.
Storage of search and recommendation history for users in the database.
Providing personalized recommendations based on user search history and preferences.
Conclusion:

This project represents a full-fledged application for convenient movie search and personalized recommendations based on user interests. It combines various aspects of software development, such as GUI development, database interaction, and data processing, to deliver a user-friendly and feature-rich experience.





