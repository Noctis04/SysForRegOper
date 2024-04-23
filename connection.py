import psycopg2
from PyQt6.QtWidgets import QMessageBox

# Подключение к базе данных
def connect_to_database():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="db_for_reg_oper",
            user="postgres",
            password="postgresql"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        QMessageBox.warning(None, 'Ошибка', f'Ошибка при подключении к базе данных:\n{str(error)}')
