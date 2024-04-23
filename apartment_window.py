import psycopg2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog
from connection import connect_to_database
from error import (correct_cod_aprtmt, contains_only_cor_text, has_correct_length, is_empty,
                   contains_only_numb, is_cor_date)

class ApartmentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица многоквартирных домов")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Код', 'Адрес', 'Год постройки', 'Этажность', 'Кол-во квартир', 'Площадь'])
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

        # Кнопка для редактирования записи
        btn_upt = QPushButton("Изменить запись")
        btn_upt.clicked.connect(self.edit_record)
        layout.addWidget(btn_upt)

        self.setLayout(layout)

        # Обновляем данные при открытии окна
        self.refresh_data()

    def refresh_data(self):
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Получаем данные из таблицы 'apartment'
            cursor.execute("SELECT * FROM public.apartment")
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
        edit_cod_num_hom = QLineEdit()
        edit_adress = QLineEdit()
        edit_year = QLineEdit()
        edit_num_of_flrs = QLineEdit()
        edit_num_of_flts = QLineEdit()
        edit_square = QLineEdit()

        # Добавляем метки и поля ввода
        layout.addWidget(QLabel("Код номера дома:"))
        layout.addWidget(edit_cod_num_hom)

        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(edit_adress)

        layout.addWidget(QLabel("Год постройки:"))
        layout.addWidget(edit_year)

        layout.addWidget(QLabel("Этажность:"))
        layout.addWidget(edit_num_of_flrs)

        layout.addWidget(QLabel("Количество квартир:"))
        layout.addWidget(edit_num_of_flts)

        layout.addWidget(QLabel("Площадь:"))
        layout.addWidget(edit_square)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_cod_num_hom.text(),
            edit_adress.text(),
            edit_year.text(),
            edit_num_of_flrs.text(),
            edit_num_of_flts.text(),
            edit_square.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec()

    def insert_record(self, cod_num_hom, adress, year, num_of_flrs, num_of_flts, square, dialog):
        # Валидация данных
        if is_empty(cod_num_hom):
            QMessageBox.warning(self, 'Ошибка', 'Не введен кадастровый номер номера дома.')
            return
        if not correct_cod_aprtmt(cod_num_hom):
            QMessageBox.warning(self, 'Ошибка', 'Кадастровый номер должен содержать только цифры и :.')
            return
        if not has_correct_length(cod_num_hom, 20, ):
            QMessageBox.warning(self, 'Ошибка', 'Неверная длина: кадастровый номер должен быть не более 20 символов.')
            return

        if is_empty(adress):
            QMessageBox.warning(self, 'Ошибка', 'Не введен адрес.')
            return
        if not contains_only_cor_text(adress):
            QMessageBox.warning(self, 'Ошибка', 'Адрес содержит недопустимые символы.')
            return
        if not has_correct_length(adress, 125):
            QMessageBox.warning(self, 'Ошибка', 'Адрес слишком длинный.')
            return

        if is_empty(year):
            QMessageBox.warning(self, 'Ошибка', 'Не введен год постройки.')
            return
        if not is_cor_date(year):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата.')
            return


        if is_empty(num_of_flrs):
            QMessageBox.warning(self, 'Ошибка', 'Не введена этажность.')
            return
        if not contains_only_numb(num_of_flrs):
            QMessageBox.warning(self, 'Ошибка', 'Этажность должна содержать только цифры.')
            return
        if not has_correct_length(num_of_flrs, 4):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большое количество этажей.')
            return

        if is_empty(num_of_flts):
            QMessageBox.warning(self, 'Ошибка', 'Не введено количество квартир.')
            return
        if not contains_only_numb(num_of_flts):
            QMessageBox.warning(self, 'Ошибка', 'Количество квартир должно содержать только цифры.')
            return
        if not has_correct_length(num_of_flts, 5):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большое количество квартир.')
            return

        if is_empty(square):
            QMessageBox.warning(self, 'Ошибка', 'Не введена площадь.')
            return
        if not contains_only_numb(square, True):
            QMessageBox.warning(self, 'Ошибка', 'Площадь должна содержать только цифры.')
            return
        if not has_correct_length(square, 8):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большая площадь.')
            return

        # Вставка данных в базу
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM public.apartment WHERE cod_num_hom = %s", (cod_num_hom,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'МКД с этим кадастровым номером уже есть в базе данных')
                return

            # Вставка новой записи
            cursor.execute("""
                INSERT INTO public.apartment (cod_num_hom, adress, year, num_of_flrs, num_of_flts, square)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cod_num_hom, adress, year, num_of_flrs, num_of_flts, square))

            connection.commit()
            cursor.close()
            connection.close()

            self.refresh_data()
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно добавлена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении записи в базу данных:\n{str(error)}')

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
            return

        cod_num_hom = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение', f'Вы уверены, что хотите удалить запись с кодом {cod_num_hom}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.apartment WHERE cod_num_hom = %s", (cod_num_hom,))
                connection.commit()
                cursor.close()
                connection.close()

                self.refresh_data()

                QMessageBox.information(self, 'Успех', 'Запись успешно удалена')

            except (Exception, psycopg2.Error) as error:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении записи из базы данных:\n{str(error)}')

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return

        cod_num_hom = self.table.item(selected_row, 0).text()
        adress = self.table.item(selected_row, 1).text()
        year = self.table.item(selected_row, 2).text()
        num_of_flrs = self.table.item(selected_row, 3).text()
        num_of_flts = self.table.item(selected_row, 4).text()
        square = self.table.item(selected_row, 5).text()

        # Окно для редактирования записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Код номера дома:"))
        edit_cod_num_hom = QLineEdit(cod_num_hom)
        edit_cod_num_hom.setReadOnly(True)
        layout.addWidget(edit_cod_num_hom)

        layout.addWidget(QLabel("Адрес:"))
        edit_adress = QLineEdit(adress)
        layout.addWidget(edit_adress)

        layout.addWidget(QLabel("Год постройки:"))
        edit_year = QLineEdit(year)
        layout.addWidget(edit_year)

        layout.addWidget(QLabel("Этажность:"))
        edit_num_of_flrs = QLineEdit(num_of_flrs)
        layout.addWidget(edit_num_of_flrs)

        layout.addWidget(QLabel("Количество квартир:"))
        edit_num_of_flts = QLineEdit(num_of_flts)
        layout.addWidget(edit_num_of_flts)

        layout.addWidget(QLabel("Площадь:"))
        edit_square = QLineEdit(square)
        layout.addWidget(edit_square)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            cod_num_hom,
            edit_adress.text(),
            edit_year.text(),
            edit_num_of_flrs.text(),
            edit_num_of_flts.text(),
            edit_square.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec()

    def update_record(self, cod_num_hom, adress, year, num_of_flrs, num_of_flts, square, dialog):
        # Валидация данных перед обновлением
        if is_empty(adress):
            QMessageBox.warning(self, 'Ошибка', 'Не введен адрес.')
            return
        if not contains_only_cor_text(adress):
            QMessageBox.warning(self, 'Ошибка', 'Адрес содержит недопустимые символы.')
            return
        if not has_correct_length(adress, 125):
            QMessageBox.warning(self, 'Ошибка', 'Адрес слишком длинный.')
            return

        if is_empty(year):
            QMessageBox.warning(self, 'Ошибка', 'Не введен год постройки.')
            return
        if not is_cor_date(year):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата.')
            return

        if is_empty(num_of_flrs):
            QMessageBox.warning(self, 'Ошибка', 'Не введена этажность.')
            return
        if not contains_only_numb(num_of_flrs):
            QMessageBox.warning(self, 'Ошибка', 'Этажность должна содержать только цифры.')
            return
        if not has_correct_length(num_of_flrs, 4):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большое количество этажей.')
            return

        if is_empty(num_of_flts):
            QMessageBox.warning(self, 'Ошибка', 'Не введено количество квартир.')
            return
        if not contains_only_numb(num_of_flts):
            QMessageBox.warning(self, 'Ошибка', 'Количество квартир должно содержать только цифры.')
            return
        if not has_correct_length(num_of_flts, 5):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большое количество квартир.')
            return

        if is_empty(square):
            QMessageBox.warning(self, 'Ошибка', 'Не введена площадь.')
            return
        if not contains_only_numb(square, True):
            QMessageBox.warning(self, 'Ошибка', 'Площадь должна содержать только цифры.')
            return
        if not has_correct_length(square, 8):
            QMessageBox.warning(self, 'Ошибка', 'Слишком большая площадь.')
            return

        # Обновление записи в базе данных
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE public.apartment
                SET adress = %s, year = %s, num_of_flrs = %s, num_of_flts = %s, square = %s
                WHERE cod_num_hom = %s
            """, (adress, year, num_of_flrs, num_of_flts, square, cod_num_hom))

            connection.commit()
            cursor.close()
            connection.close()

            self.refresh_data()
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно изменена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при изменении записи в базе данных:\n{str(error)}')
