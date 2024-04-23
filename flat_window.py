import psycopg2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog
from connection import connect_to_database
from error import (correct_cod_aprtmt, has_correct_length, is_empty, contains_only_numb)

class FlatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица квартир")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Изменяем количество столбцов
        self.table.setHorizontalHeaderLabels(['Код квартиры', 'Id Владелеца', 'Код многоквартирного дома', 'Номер', 'Этаж', 'Площадь'])  # Изменяем заголовки столбцов
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
            cursor.execute("SELECT * FROM public.flat")
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
        lbl_cod_flt = QLabel("Код квартиры:")
        edit_cod_flt = QLineEdit()
        layout.addWidget(lbl_cod_flt)
        layout.addWidget(edit_cod_flt)

        lbl_owner_uid = QLabel("Id владелеца:")
        edit_owner_uid = QLineEdit()
        layout.addWidget(lbl_owner_uid)
        layout.addWidget(edit_owner_uid)

        lbl_aprtmt_uid = QLabel("Код многоквартирного дома:")
        edit_aprtmt_uid = QLineEdit()
        layout.addWidget(lbl_aprtmt_uid)
        layout.addWidget(edit_aprtmt_uid)

        lbl_nom_flt = QLabel("Номер квартиры:")
        edit_nom_flt = QLineEdit()
        layout.addWidget(lbl_nom_flt)
        layout.addWidget(edit_nom_flt)

        lbl_floor_flt = QLabel("Этаж:")
        edit_floor_flt = QLineEdit()
        layout.addWidget(lbl_floor_flt)
        layout.addWidget(edit_floor_flt)

        lbl_square_flt = QLabel("Площадь:")
        edit_square_flt = QLineEdit()
        layout.addWidget(lbl_square_flt)
        layout.addWidget(edit_square_flt)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_cod_flt.text(),
            edit_owner_uid.text(),
            edit_aprtmt_uid.text(),
            edit_nom_flt.text(),
            edit_floor_flt.text(),
            edit_square_flt.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec()

    def insert_record(self, cod_flt, owner_uid, aprtmt_uid, nom_flt, floor_flt, square_flt, dialog):
        if is_empty(cod_flt):
            QMessageBox.warning(self, 'Ошибка', 'Не введен кадастровый номер номера квартиры.')
            return
        if not correct_cod_aprtmt(cod_flt):
            QMessageBox.warning(self, 'Ошибка', 'Кадастровый номер должен содержать только цифры и :.')
            return
        if not has_correct_length(cod_flt, 20):
            QMessageBox.warning(self, 'Ошибка', 'Неверная длина: кадастровый номер должен быть не более 20 символов.')
            return

        if is_empty(owner_uid):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца не может быть пустым.')
            return
        if not contains_only_numb(owner_uid):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца должен состоять только из цифр.')
            return
        if not has_correct_length(owner_uid, 10, True):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца должен состоять из 10 цифр.')
            return

        if is_empty(aprtmt_uid):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома не может быть пустым.')
            return
        if not correct_cod_aprtmt(aprtmt_uid):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома должен состоять из цифр и :.')
            return
        if not has_correct_length(aprtmt_uid, 20):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома может состоять не более чем из 20 символов.')
            return

        if is_empty(nom_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры не может быть пустым.')
            return
        if not contains_only_numb(nom_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры должен быть числом.')
            return
        if not has_correct_length(nom_flt, 5):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры слишком большой.')
            return

        if is_empty(floor_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа не может быть пустым.')
            return
        if not contains_only_numb(floor_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа должен быть числом.')
            return
        if not has_correct_length(floor_flt, 5):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа слишком большой.')
            return

        if is_empty(square_flt):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры не может не иметь значения.')
            return
        if not contains_only_numb(square_flt, True):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры должна быть числом.')
            return
        if not has_correct_length(square_flt, 7):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры слишком большая.')
            return
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Проверка уникальности UID
            cursor.execute("SELECT * FROM public.flat WHERE cod_flt = %s AND owner_uid = %s AND aprtmt_uid = %s",
                           (cod_flt, owner_uid, aprtmt_uid))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'Квартира с этим UID уже существует')
                return

            cursor.execute("SELECT * FROM public.flat WHERE cod_flt = %s ", (cod_flt,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'Квартира с этим кадастровым номером уже есть в базе данных')
                return

            cursor.execute("SELECT * FROM public.owner WHERE uid = %s", (owner_uid,))
            if cursor.fetchone() is None:
                QMessageBox.warning(self, 'Ошибка', 'Владелеца квартиры с этим UID нет базе данных')
                return

            cursor.execute("SELECT * FROM public.apartment WHERE cod_num_hom = %s", (aprtmt_uid,))
            apartment_record = cursor.fetchone()
            if apartment_record is None:
                QMessageBox.warning(self, 'Ошибка', 'МКД с этим кадастровым номером нет в базе данных')
                return

            total_floors = apartment_record[3]
            total_apartments = apartment_record[4]
            total_square = apartment_record[5]

            if int(nom_flt) > int(total_apartments):
                QMessageBox.warning(self, 'Ошибка', 'Номер квартиры превышает общее количество квартир в доме.')
                return

            if int(floor_flt) > int(total_floors):
                QMessageBox.warning(self, 'Ошибка', 'Этаж превышает количество этажей в доме.')
                return

            if float(square_flt) > float(total_square):
                QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры превышает площадь многоквартирного дома.')
                return


            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                INSERT INTO public.flat (cod_flt, owner_uid, aprtmt_uid, nom_flt, floor_flt, square_flt)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cod_flt, owner_uid, aprtmt_uid, nom_flt, floor_flt, square_flt))

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

        cod_flt = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с кодом {cod_flt}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.flat WHERE cod_flt = %s", (cod_flt,))
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
        cod_flt = self.table.item(selected_row, 0).text()
        owner_uid = self.table.item(selected_row, 1).text()
        aprtmt_uid = self.table.item(selected_row, 2).text()
        nom_flt = self.table.item(selected_row, 3).text()
        floor_flt = self.table.item(selected_row, 4).text()
        square_flt = self.table.item(selected_row, 5).text()

        # Окно для редактирования записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных с заполненными значениями
        lbl_cod_flt = QLabel("Код квартиры:")
        edit_cod_flt = QLineEdit(cod_flt)
        edit_cod_flt.setReadOnly(True)
        layout.addWidget(lbl_cod_flt)
        layout.addWidget(edit_cod_flt)

        lbl_owner_uid = QLabel("Владелец:")
        edit_owner_uid = QLineEdit(owner_uid)
        layout.addWidget(lbl_owner_uid)
        layout.addWidget(edit_owner_uid)

        lbl_aprtmt_uid = QLabel("Апартамент:")
        edit_aprtmt_uid = QLineEdit(aprtmt_uid)
        edit_aprtmt_uid.setReadOnly(True)
        layout.addWidget(lbl_aprtmt_uid)
        layout.addWidget(edit_aprtmt_uid)

        lbl_nom_flt = QLabel("Номер квартиры:")
        edit_nom_flt = QLineEdit(nom_flt)
        layout.addWidget(lbl_nom_flt)
        layout.addWidget(edit_nom_flt)

        lbl_floor_flt = QLabel("Этаж:")
        edit_floor_flt = QLineEdit(floor_flt)
        layout.addWidget(lbl_floor_flt)
        layout.addWidget(edit_floor_flt)

        lbl_square_flt = QLabel("Площадь:")
        edit_square_flt = QLineEdit(square_flt)
        layout.addWidget(lbl_square_flt)
        layout.addWidget(edit_square_flt)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            cod_flt,
            edit_owner_uid.text(),
            edit_aprtmt_uid.text(),
            edit_nom_flt.text(),
            edit_floor_flt.text(),
            edit_square_flt.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec()

    def update_record(self, cod_flt, owner_uid, aprtmt_uid, nom_flt, floor_flt, square_flt, dialog):
        if is_empty(owner_uid):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца не может быть пустым.')
            return
        if not contains_only_numb(owner_uid):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца должен состоять только из цифр.')
            return
        if not has_correct_length(owner_uid, 10, True):
            QMessageBox.warning(self, 'Ошибка', 'Id владельца должен состоять из 10 цифр.')
            return

        if is_empty(aprtmt_uid):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома не может быть пустым.')
            return
        if not correct_cod_aprtmt(aprtmt_uid):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома должен состоять из цифр и :.')
            return
        if not has_correct_length(aprtmt_uid, 20):
            QMessageBox.warning(self, 'Ошибка', 'Код многоквартирного дома может состоять не более чем из 20 символов.')
            return

        if is_empty(nom_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры не может быть пустым.')
            return
        if not contains_only_numb(nom_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры должен быть числом.')
            return
        if not has_correct_length(nom_flt, 5):
            QMessageBox.warning(self, 'Ошибка', 'Номер квартиры слишком большой.')
            return

        if is_empty(floor_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа не может быть пустым.')
            return
        if not contains_only_numb(floor_flt):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа должен быть числом.')
            return
        if not has_correct_length(floor_flt, 5):
            QMessageBox.warning(self, 'Ошибка', 'Номер этажа слишком большой.')
            return

        if is_empty(square_flt):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры не может не иметь значения.')
            return
        if not contains_only_numb(square_flt, True):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры должна быть числом.')
            return
        if not has_correct_length(square_flt, 7):
            QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры слишком большая.')
            return
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM public.owner WHERE uid = %s", (owner_uid,))
            if cursor.fetchone() is None:
                QMessageBox.warning(self, 'Ошибка', 'Владелеца квартиры с этим UID нет базе данных')
                return

            cursor.execute("SELECT * FROM public.apartment WHERE cod_num_hom = %s", (aprtmt_uid,))
            apartment_record = cursor.fetchone()
            total_floors = apartment_record[3]
            total_apartments = apartment_record[4]
            total_square = apartment_record[5]

            if int(nom_flt) > int(total_apartments):
                QMessageBox.warning(self, 'Ошибка', 'Номер квартиры превышает общее количество квартир в доме.')
                return

            if int(floor_flt) > int(total_floors):
                QMessageBox.warning(self, 'Ошибка', 'Этаж превышает количество этажей в доме.')
                return

            if float(square_flt) > float(total_square):
                QMessageBox.warning(self, 'Ошибка', 'Площадь квартиры превышает площадь многоквартирного дома.')
                return

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                UPDATE public.flat
                SET owner_uid = %s, aprtmt_uid = %s, nom_flt = %s, floor_flt = %s, square_flt = %s
                WHERE cod_flt = %s
            """, (owner_uid, aprtmt_uid, nom_flt, floor_flt, square_flt, cod_flt))

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
