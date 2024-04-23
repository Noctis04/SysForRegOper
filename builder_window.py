import re
import psycopg2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QMessageBox, QDialog
)
from connection import connect_to_database
from error import contains_only_numb, contains_only_cor_text, has_correct_length, is_empty


class BuilderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица строительных организаций")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['INN организации', 'Название организации', 'Телефон', 'Адрес'])
        layout.addWidget(self.table)

        # Кнопки управления
        btn_refresh = QPushButton("Обновить данные")
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)

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
        self.refresh_data()

    def refresh_data(self):
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM public.builder")
            rows = cursor.fetchall()

            self.table.setRowCount(0)

            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

            # Подгоняем ширину столбцов после обновления данных
            self.table.resizeColumnsToContents()

            cursor.close()
            connection.close()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при получении данных:\n{str(error)}')

    def add_record(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить запись")

        layout = QVBoxLayout()

        # Поля ввода
        edit_inn_org = QLineEdit()
        edit_name_of_org = QLineEdit()
        edit_ph_numb = QLineEdit()
        edit_adress = QLineEdit()

        layout.addWidget(QLabel("INN организации:"))
        layout.addWidget(edit_inn_org)

        layout.addWidget(QLabel("Название организации:"))
        layout.addWidget(edit_name_of_org)

        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(edit_ph_numb)

        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(edit_adress)

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
        dialog.exec()

    def insert_record(self, inn_org, name_of_org, ph_numb, adress, dialog):
        # Валидация полей
        if is_empty(inn_org):
            QMessageBox.warning(self, 'Ошибка', "Не введён INN организации.")
            return
        if not contains_only_numb(inn_org):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: INN должен состоять только из цифр.")
            return
        if not has_correct_length(inn_org, 12, True):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: INN должен состоять из 12 цифр.")
            return
        if is_empty(name_of_org):
            QMessageBox.warning(self, 'Ошибка', "Не введено название организации.")
            return
        if not contains_only_cor_text(name_of_org):
            QMessageBox.warning(self, 'Ошибка',
                                "Некорректные символы: название органирзации содержит некорректные символы.")
            return
        if not has_correct_length(name_of_org, 50):
            QMessageBox.warning(self, 'Ошибка',
                                "Неверная длина: название организации не должно быть длиннее 50 симоволов.")
            return
        if is_empty(ph_numb):
            QMessageBox.warning(self, 'Ошибка', "Не введён номер телефона.")
            return
        if not contains_only_numb(ph_numb):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: телефон должен состоять только из цифр.")
            return
        if not has_correct_length(ph_numb, 11, True):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: телефон должен состоять из 10 цифр.")
            return
        if is_empty(adress):
            QMessageBox.warning(self, 'Ошибка', "Не введён адрес.")
            return
        if not contains_only_cor_text(adress):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: адрес содержит некорректные символы.")
            return
        if not has_correct_length(adress, 125, ):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: адрес не должно быть длиннее 125 симоволов.")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Проверка уникальности UID
            cursor.execute("SELECT * FROM public.builder WHERE inn_org = %s", (inn_org,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'Организация с этим INN уже есть в базе данных')
                return

            # Вставка записи
            cursor.execute("""
                INSERT INTO public.builder (inn_org, name_of_org, ph_numb, adress)
                VALUES (%s, %s, %s, %s)
            """, (inn_org, name_of_org, ph_numb, adress))

            connection.commit()
            cursor.close()
            connection.close()

            # Обновление данных и закрытие диалога
            self.refresh_data()
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно добавлена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении записи:\n{str(error)}')

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
            return

        inn_org = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с INN {inn_org}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM public.builder WHERE inn_org = %s", (inn_org,))
                connection.commit()
                cursor.close()
                connection.close()

                self.refresh_data()

                QMessageBox.information(self, 'Успех', 'Запись успешно удалена')

            except (Exception, psycopg2.Error) as error:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении записи:\n{str(error)}')

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return

        inn_org = self.table.item(selected_row, 0).text()
        name_of_org = self.table.item(selected_row, 1).text()
        ph_numb = self.table.item(selected_row, 2).text()
        adress = self.table.item(selected_row, 3).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить запись")

        layout = QVBoxLayout()

        # Поля ввода
        edit_inn_org = QLineEdit(inn_org)
        edit_inn_org.setReadOnly(True)
        layout.addWidget(QLabel("INN организации:"))
        layout.addWidget(edit_inn_org)

        edit_name_of_org = QLineEdit(name_of_org)
        layout.addWidget(QLabel("Название организации:"))
        layout.addWidget(edit_name_of_org)

        edit_ph_numb = QLineEdit(ph_numb)
        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(edit_ph_numb)

        edit_adress = QLineEdit(adress)
        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(edit_adress)

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
        dialog.exec()

    def update_record(self, inn_org, name_of_org, ph_numb, adress, dialog):
        if is_empty(name_of_org):
            QMessageBox.warning(self, 'Ошибка', "Не введено название организации.")
            return
        if not contains_only_cor_text(name_of_org):
            QMessageBox.warning(self, 'Ошибка',
                                "Некорректные символы: название органирзации содержит некорректные символы.")
            return
        if not has_correct_length(name_of_org, 50):
            QMessageBox.warning(self, 'Ошибка',
                                "Неверная длина: название организации не должно быть длиннее 50 симоволов.")
            return
        if is_empty(ph_numb):
            QMessageBox.warning(self, 'Ошибка', "Не введён номер телефона.")
            return
        if not contains_only_numb(ph_numb):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: телефон должен состоять только из цифр.")
            return
        if not has_correct_length(ph_numb, 11, True):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: телефон должен состоять из 10 цифр.")
            return
        if is_empty(adress):
            QMessageBox.warning(self, 'Ошибка', "Не введён адрес.")
            return
        if not contains_only_cor_text(adress):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: адрес содержит некорректные символы.")
            return
        if not has_correct_length(adress, 125):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: адрес не должно быть длиннее 125 симоволов.")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE public.builder
                SET name_of_org = %s, ph_numb = %s, adress = %s
                WHERE inn_org = %s
            """, (name_of_org, ph_numb, adress, inn_org))

            connection.commit()
            cursor.close()
            connection.close()

            self.refresh_data()
            dialog.close()

            QMessageBox.information(self, 'Успех', 'Запись успешно изменена')

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при изменении записи:\n{str(error)}')
