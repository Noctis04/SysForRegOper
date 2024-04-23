import psycopg2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog
from connection import connect_to_database
from error import ( contains_only_cor_text, has_correct_length, is_empty,
                   contains_only_numb)


class OwnerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица владельцев квартир")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['UID', 'ФИО', 'Телефон'])
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
            cursor.execute("SELECT * FROM public.owner")
            rows = cursor.fetchall()

            # Очищаем таблицу перед обновлением данных
            self.table.setRowCount(0)

            # Заполняем таблицу данными
            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

            # Подгоняем ширину столбцов после обновления данных
            self.table.resizeColumnsToContents()

            cursor.close()
            connection.close()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при получении данных из базы данных:\n{str(error)}')

    def add_record(self):
        # Окно для ввода новой записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных
        lbl_uid = QLabel("UID:")
        edit_uid = QLineEdit()
        layout.addWidget(lbl_uid)
        layout.addWidget(edit_uid)

        lbl_fio = QLabel("ФИО:")
        edit_fio = QLineEdit()
        layout.addWidget(lbl_fio)
        layout.addWidget(edit_fio)

        lbl_ph_numb = QLabel("Телефон:")
        edit_ph_numb = QLineEdit()
        layout.addWidget(lbl_ph_numb)
        layout.addWidget(edit_ph_numb)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_uid.text(),
            edit_fio.text(),
            edit_ph_numb.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec()

    def insert_record(self, uid, fio, ph_numb, dialog):
        if is_empty(uid):
            QMessageBox.warning(self, 'Ошибка', 'Не введен UID.')
            return
        if not contains_only_numb(uid):
            QMessageBox.warning(self, 'Ошибка', 'UID должен содержать только цифры.')
            return
        if not has_correct_length(uid, 10, True):
            QMessageBox.warning(self, 'Ошибка', 'UID должно содержать 10 символов.')
            return

        if is_empty(fio):
            QMessageBox.warning(self, 'Ошибка', 'Не введено ФИО.')
            return
        if not contains_only_cor_text(fio):
            QMessageBox.warning(self, 'Ошибка', 'ФИО содержит некорректные символы.')
            return
        if not has_correct_length(fio, 50):
            QMessageBox.warning(self, 'Ошибка', 'Слишком длинное ФИО.')
            return

        if is_empty(ph_numb):
            QMessageBox.warning(self, 'Ошибка', 'Не введен номер телефона.')
            return
        if not contains_only_numb(ph_numb):
            QMessageBox.warning(self, 'Ошибка', 'Номер телефона должен содержать только цифры.')
            return
        if not has_correct_length(ph_numb, 11, True):
            QMessageBox.warning(self, 'Ошибка', 'Неверная длина номера телефона.')
            return
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Проверка уникальности UID
            cursor.execute("SELECT * FROM public.owner WHERE uid = %s", (uid,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'Владелец квартиры с этим UID уже есть в базе данных')
                return

            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                INSERT INTO public.owner (uid, fio, ph_numb)
                VALUES (%s, %s, %s)
            """, (uid, fio, ph_numb))

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

        uid = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с UID {uid}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.owner WHERE uid = %s", (uid,))
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
        uid = self.table.item(selected_row, 0).text()
        fio = self.table.item(selected_row, 1).text()
        ph_numb = self.table.item(selected_row, 2).text()

        # Окно для редактирования записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных с заполненными значениями
        lbl_uid = QLabel("UID:")
        edit_uid = QLineEdit(uid)
        edit_uid.setReadOnly(True)
        layout.addWidget(lbl_uid)
        layout.addWidget(edit_uid)

        lbl_fio = QLabel("ФИО:")
        edit_fio = QLineEdit(fio)
        layout.addWidget(lbl_fio)
        layout.addWidget(edit_fio)

        lbl_ph_numb = QLabel("Телефон:")
        edit_ph_numb = QLineEdit(ph_numb)
        layout.addWidget(lbl_ph_numb)
        layout.addWidget(edit_ph_numb)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            uid,
            edit_fio.text(),
            edit_ph_numb.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec()

    def update_record(self, uid, fio, ph_numb, dialog):

        if is_empty(fio):
            QMessageBox.warning(self, 'Ошибка', 'Не введено ФИО.')
            return
        if not contains_only_cor_text(fio):
            QMessageBox.warning(self, 'Ошибка', 'ФИО содержит некорректные символы.')
            return
        if not has_correct_length(fio, 50):
            QMessageBox.warning(self, 'Ошибка', 'Слишком длинное ФИО.')
            return

        if is_empty(ph_numb):
            QMessageBox.warning(self, 'Ошибка', 'Не введен номер телефона.')
            return
        if not contains_only_numb(ph_numb):
            QMessageBox.warning(self, 'Ошибка', 'Номер телефона должен содержать только цифры.')
            return
        if not has_correct_length(ph_numb, 11, True):
            QMessageBox.warning(self, 'Ошибка', 'Неверная длина номера телефона.')
            return
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                UPDATE public.owner
                SET fio = %s, ph_numb = %s
                WHERE uid = %s
            """, (fio, ph_numb, uid))

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
