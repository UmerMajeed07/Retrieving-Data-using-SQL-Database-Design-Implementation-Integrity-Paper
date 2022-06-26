import sqlite3
from sqlite3 import Error


class Database:

    @staticmethod
    def create_connection() -> object:
        """
          create a database connection to the SQLite database
          specified by the db_file

          Returns:
              Connection object or None
        """
        db_file = 'database.db'
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn
