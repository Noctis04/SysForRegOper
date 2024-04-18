import psycopg2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
                             QMessageBox, QDialog)
from connection import connect_to_database


class RepairWorkWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица ремонтных работ")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Код работы', 'Тип работы'])
        layout.addWidget(self.table)

        # Кнопка для обновления данных в таблице
        btn_refresh = QPushButton("Обновить данные")
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)

        # Кнопка для добавления новой записи
        btn_add = QPushButton("Добавить запись")
        btn_add.clicked.connect(self.add_record)
        layout.addWidget(btn_add)

        # Кнопка для удаления записи
        btn_del = QPushButton("Удалить запись")
        btn_del.clicked.connect(self.delete_record)
        layout.addWidget(btn_del)

        # Кнопка для изменения записи
        btn_upt = QPushButton("Изменить запись")
        btn_upt.clicked.connect(self.edit_record)
        layout.addWidget(btn_upt)

        self.setLayout(layout)

        # Обновляем данные при открытии окна
        self.refresh_data()

    def refresh_data(self):
        # Подключаемся к базе данных и получаем данные

        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM public.repair_work")
            rows = cursor.fetchall()

            # Очищаем таблицу перед обновлением данных
            self.table.setRowCount(0)

            # Заполняем таблицу данными
            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

            cursor.close()
            connection.close()

        except psycopg2.Error as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при получении данных из базы данных:\n{str(error)}')

    def add_record(self):
        # Окно для ввода новой записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных
        lbl_cod_rep_work = QLabel("Код работы:")
        edit_cod_rep_work = QLineEdit()
        layout.addWidget(lbl_cod_rep_work)
        layout.addWidget(edit_cod_rep_work)

        lbl_type_of_work = QLabel("Тип работы:")
        edit_type_of_work = QLineEdit()
        layout.addWidget(lbl_type_of_work)
        layout.addWidget(edit_type_of_work)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_cod_rep_work.text(),
            edit_type_of_work.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec_()

    def insert_record(self, cod_rep_work, type_of_work, dialog):

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                    INSERT INTO public.repair_work (cod_rep_work, type_of_work)
                    VALUES (%s, %s)
                """, (cod_rep_work, type_of_work))

            connection.commit()
            cursor.close()
            connection.close()

            # Обновляем данные в таблице
            self.refresh_data()

            # Закрываем окно добавления записи
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно добавлена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении записи в базу данных:\n{str(error)}')

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
            return

        cod_rep_work = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с кодом работы {cod_rep_work}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.repair_work WHERE cod_rep_work = %s", (cod_rep_work,))
                connection.commit()
                cursor.close()
                connection.close()
                # Обновляем данные в таблице
                self.refresh_data()
                QMessageBox.information(self, 'Успех', 'Запись успешно удалена')

            except (Exception, psycopg2.Error) as error:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении записи из базы данных:\n{str(error)}')

    def edit_record(self):
        # Получаем выбранную строку
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return

        # Получаем данные выбранной строки
        cod_rep_work = self.table.item(selected_row, 0).text()
        type_of_work = self.table.item(selected_row, 1).text()

        # Окно для редактирования записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных с заполненными значениями
        lbl_cod_rep_work = QLabel("Код работы:")
        edit_cod_rep_work = QLineEdit(cod_rep_work)
        edit_cod_rep_work.setReadOnly(True)
        layout.addWidget(lbl_cod_rep_work)
        layout.addWidget(edit_cod_rep_work)

        lbl_type_of_work = QLabel("Тип работы:")
        edit_type_of_work = QLineEdit(type_of_work)
        layout.addWidget(lbl_type_of_work)
        layout.addWidget(edit_type_of_work)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            cod_rep_work,
            edit_type_of_work.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec_()

    def update_record(self, cod_rep_work, type_of_work, dialog):
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                    UPDATE public.repair_work
                    SET type_of_work = %s
                    WHERE cod_rep_work = %s
                """, (type_of_work, cod_rep_work))

            connection.commit()
            cursor.close()
            connection.close()

            # Обновляем данные в таблице
            self.refresh_data()

            # Закрываем окно редактирования записи
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно изменена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при изменении записи в базе данных:\n{str(error)}')
