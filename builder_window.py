import psycopg2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, \
    QMessageBox, QDialog
from connection import connect_to_database


class BuilderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица строительных организаций")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['INN организации', 'Название организации', 'Телефон', 'Адрес'])
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
            cursor.execute("SELECT * FROM public.builder")
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
        lbl_inn_org = QLabel("INN организации:")
        edit_inn_org = QLineEdit()
        layout.addWidget(lbl_inn_org)
        layout.addWidget(edit_inn_org)

        lbl_name_of_org = QLabel("Название организации:")
        edit_name_of_org = QLineEdit()
        layout.addWidget(lbl_name_of_org)
        layout.addWidget(edit_name_of_org)

        lbl_ph_numb = QLabel("Телефон:")
        edit_ph_numb = QLineEdit()
        layout.addWidget(lbl_ph_numb)
        layout.addWidget(edit_ph_numb)

        lbl_adress = QLabel("Адрес:")
        edit_adress = QLineEdit()
        layout.addWidget(lbl_adress)
        layout.addWidget(edit_adress)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_inn_org.text(),
            edit_name_of_org.text(),
            edit_ph_numb.text(),
            edit_adress.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec_()

    def insert_record(self, inn_org, name_of_org, ph_numb, adress, dialog):
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                INSERT INTO public.builder (inn_org, name_of_org, ph_numb, adress)
                VALUES (%s, %s, %s, %s)
            """, (inn_org, name_of_org, ph_numb, adress))

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

        inn_org = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с INN {inn_org}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.builder WHERE inn_org = %s", (inn_org,))
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
        inn_org = self.table.item(selected_row, 0).text()
        name_of_org = self.table.item(selected_row, 1).text()
        ph_numb = self.table.item(selected_row, 2).text()
        adress = self.table.item(selected_row, 3).text()

        # Окно для редактирования записи
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        # Добавляем поля для ввода данных с заполненными значениями
        lbl_inn_org = QLabel("INN организации:")
        edit_inn_org = QLineEdit(inn_org)
        edit_inn_org.setReadOnly(True)
        layout.addWidget(lbl_inn_org)
        layout.addWidget(edit_inn_org)

        lbl_name_of_org = QLabel("Название организации:")
        edit_name_of_org = QLineEdit(name_of_org)
        layout.addWidget(lbl_name_of_org)
        layout.addWidget(edit_name_of_org)

        lbl_ph_numb = QLabel("Телефон:")
        edit_ph_numb = QLineEdit(ph_numb)
        layout.addWidget(lbl_ph_numb)
        layout.addWidget(edit_ph_numb)

        lbl_adress = QLabel("Адрес:")
        edit_adress = QLineEdit(adress)
        layout.addWidget(lbl_adress)
        layout.addWidget(edit_adress)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            inn_org,
            edit_name_of_org.text(),
            edit_ph_numb.text(),
            edit_adress.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec_()

    def update_record(self, inn_org, name_of_org, ph_numb, adress, dialog):
        try:
            # Подключаемся к базе данных
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                UPDATE public.builder
                SET name_of_org = %s, ph_numb = %s, adress = %s
                WHERE inn_org = %s
            """, (name_of_org, ph_numb, adress, inn_org))

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
