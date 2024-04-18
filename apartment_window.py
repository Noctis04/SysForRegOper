import psycopg2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog
from connection import connect_to_database

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
        self.table.setHorizontalHeaderLabels(['Код многоквартирного дома', 'Адрес', 'Год постройки', 'Этажность', 'Кол-во квартир', 'Площадь'])
        layout.addWidget(self.table)

        # Кнопка для обновления данных в таблице
        btn_refresh = QPushButton("Обновить данные")
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)

        # Кнопка для добавления новой записи
        btn_add = QPushButton("Добавить запись")
        btn_add.clicked.connect(self.add_record)
        layout.addWidget(btn_add)

        btn_del = QPushButton("Удалить запись")
        btn_del.clicked.connect(self.delete_record)
        layout.addWidget(btn_del)

        btn_upt = QPushButton("Изменить запись")
        btn_upt.clicked.connect(self.edit_record)
        layout.addWidget(btn_upt)

        self.setLayout(layout)

        # Обновляем данные при открытии окна
        self.refresh_data()

    def refresh_data(self):
        # Подключаемся к базе данных
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
        lbl_cod_num_hom = QLabel("Код номера мкд:")
        edit_cod_num_hom = QLineEdit()
        layout.addWidget(lbl_cod_num_hom)
        layout.addWidget(edit_cod_num_hom)

        lbl_adress = QLabel("Адрес:")
        edit_adress = QLineEdit()
        layout.addWidget(lbl_adress)
        layout.addWidget(edit_adress)

        lbl_year = QLabel("Год постройки:")
        edit_year = QLineEdit()
        layout.addWidget(lbl_year)
        layout.addWidget(edit_year)

        lbl_num_of_flrs = QLabel("Этажность:")
        edit_num_of_flrs = QLineEdit()
        layout.addWidget(lbl_num_of_flrs)
        layout.addWidget(edit_num_of_flrs)

        lbl_num_of_flts = QLabel("Количество квартир:")
        edit_num_of_flts = QLineEdit()
        layout.addWidget(lbl_num_of_flts)
        layout.addWidget(edit_num_of_flts)

        lbl_square = QLabel("Площадь:")
        edit_square = QLineEdit()
        layout.addWidget(lbl_square)
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
        dialog.exec_()

    def insert_record(self, cod_num_hom, adress, year, num_of_flrs, num_of_flts, square, dialog):
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                INSERT INTO public.apartment (cod_num_hom, adress, year, num_of_flrs, num_of_flts, square)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cod_num_hom, adress, year, num_of_flrs, num_of_flts, square))

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

        cod_num_hom = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с кодом {cod_num_hom}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:

                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.apartment WHERE cod_num_hom = %s", (cod_num_hom,))
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

        # Добавляем поля для ввода данных с заполненными значениями
        lbl_cod_num_hom = QLabel("Код номера дома:")
        edit_cod_num_hom = QLineEdit(cod_num_hom)
        edit_cod_num_hom.setReadOnly(True)
        layout.addWidget(lbl_cod_num_hom)
        layout.addWidget(edit_cod_num_hom)

        lbl_adress = QLabel("Адрес:")
        edit_adress = QLineEdit(adress)
        layout.addWidget(lbl_adress)
        layout.addWidget(edit_adress)

        lbl_year = QLabel("Год постройки:")
        edit_year = QLineEdit(year)
        layout.addWidget(lbl_year)
        layout.addWidget(edit_year)

        lbl_num_of_flrs = QLabel("Этажность:")
        edit_num_of_flrs = QLineEdit(num_of_flrs)
        layout.addWidget(lbl_num_of_flrs)
        layout.addWidget(edit_num_of_flrs)

        lbl_num_of_flts = QLabel("Количество квартир:")
        edit_num_of_flts = QLineEdit(num_of_flts)
        layout.addWidget(lbl_num_of_flts)
        layout.addWidget(edit_num_of_flts)

        lbl_square = QLabel("Площадь:")
        edit_square = QLineEdit(square)
        layout.addWidget(lbl_square)
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
        dialog.exec_()

    def update_record(self, cod_num_hom, adress, year, num_of_flrs, num_of_flts, square, dialog):
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                UPDATE public.apartment
                SET adress = %s, year = %s, num_of_flrs = %s, num_of_flts = %s, square = %s
                WHERE cod_num_hom = %s
            """, (adress, year, num_of_flrs, num_of_flts, square, cod_num_hom))

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