import psycopg2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QDialog
from connection import connect_to_database
from error import (correct_cod_aprtmt, contains_only_cor_text, has_correct_length, is_empty,
                   contains_only_numb, is_cor_date)

class CurrentRepairWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таблица текущих ремонтных работ")
        self.resize(1280, 720)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Код работы', 'ИНН организации', 'Код номера дома', 'Наименование работы', 'Дата начала', 'Дата окончания'])
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
            cursor.execute("SELECT * FROM public.current_repair")
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

        lbl_inn_org = QLabel("ИНН организации:")
        edit_inn_org = QLineEdit()
        layout.addWidget(lbl_inn_org)
        layout.addWidget(edit_inn_org)

        lbl_cod_num_hom = QLabel("Код номера дома:")
        edit_cod_num_hom = QLineEdit()
        layout.addWidget(lbl_cod_num_hom)
        layout.addWidget(edit_cod_num_hom)

        lbl_name_of_work = QLabel("Наименование работы:")
        edit_name_of_work = QLineEdit()
        layout.addWidget(lbl_name_of_work)
        layout.addWidget(edit_name_of_work)

        lbl_date_start = QLabel("Дата начала:")
        edit_date_start = QLineEdit()
        layout.addWidget(lbl_date_start)
        layout.addWidget(edit_date_start)

        lbl_date_end = QLabel("Дата окончания:")
        edit_date_end = QLineEdit()
        layout.addWidget(lbl_date_end)
        layout.addWidget(edit_date_end)

        # Кнопка для добавления записи
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(lambda: self.insert_record(
            edit_cod_rep_work.text(),
            edit_inn_org.text(),
            edit_cod_num_hom.text(),
            edit_name_of_work.text(),
            edit_date_start.text(),
            edit_date_end.text(),
            dialog
        ))
        layout.addWidget(btn_add)

        dialog.setLayout(layout)
        dialog.exec()

    def insert_record(self, cod_rep_work, inn_org, cod_num_hom, name_of_work, date_start, date_end, dialog):
        if is_empty(cod_rep_work):
            QMessageBox.warning(self, 'Ошибка', 'Код работы не может быть пустым.')
            return
        if not contains_only_numb(cod_rep_work):
            QMessageBox.warning(self, 'Ошибка', 'Код работы должен содержать только цифры.')
            return
        if not has_correct_length(cod_rep_work, 12, True):
            QMessageBox.warning(self, 'Ошибка', 'Код работы должен быть длиной 12 символов.')
            return

        if is_empty(inn_org):
            QMessageBox.warning(self, 'Ошибка', "Не введён INN организации.")
            return
        if not contains_only_numb(inn_org):
            QMessageBox.warning(self, 'Ошибка', "Некорректные символы: INN должен состоять только из цифр.")
            return
        if not has_correct_length(inn_org, 12, True):
            QMessageBox.warning(self, 'Ошибка', "Неверная длина: INN должен состоять из 12 цифр.")
            return

        if is_empty(cod_num_hom):
            QMessageBox.warning(self, 'Ошибка', 'Не введен кадастровый номер номера дома.')
            return
        if not correct_cod_aprtmt(cod_num_hom):
            QMessageBox.warning(self, 'Ошибка', 'Кадастровый номер должен содержать только цифры и :.')
            return
        if not has_correct_length(cod_num_hom, 20, ):
            QMessageBox.warning(self, 'Ошибка', 'Неверная длина: кадастровый номер должен быть не более 20 символов.')
            return

        if is_empty(name_of_work):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы не может быть пустым.')
            return
        if not contains_only_cor_text(name_of_work):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы содержит некорректные символы.')
            return
        if not has_correct_length(name_of_work, 50):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы должен быть длиной не более 50 символов.')

        if is_empty(date_start):
            QMessageBox.warning(self, 'Ошибка', 'Не введен дата начала ремонтных работ.')
            return
        if not is_cor_date(date_start):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата начала ремонтных работ.')
            return

        if is_empty(date_end):
            QMessageBox.warning(self, 'Ошибка', 'Не введен дата окончания ремонтных работ.')
            return
        if not is_cor_date(date_end):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата окончания ремонтных работ.')
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM public.current_repair WHERE cod_rep_work = %s AND inn_org = %s AND cod_num_hom = %s",
                           (cod_rep_work, inn_org, cod_num_hom))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self, 'Ошибка', 'Текущий ремонт с этим UID уже существует')
                return

            cursor.execute("SELECT * FROM public.apartment WHERE cod_num_hom = %s", (cod_num_hom,))
            if cursor.fetchone() is None:
                QMessageBox.warning(self, 'Ошибка', 'МКД с этим кадастровым номером нет в базе данных')
                return

            cursor.execute("SELECT * FROM public.repair_work WHERE cod_rep_work = %s", (cod_rep_work,))
            if cursor.fetchone() is None:
                QMessageBox.warning(self, 'Ошибка', 'Ремонтной работы с этим кодом нет в базе данных')
                return

            cursor.execute("SELECT * FROM public.builder WHERE inn_org = %s", (inn_org,))
            if cursor.fetchone() is None:
                QMessageBox.warning(self, 'Ошибка', 'Строительной организации с таким ИНН нет в базе данных')
                return

            # Выполняем SQL-запрос для добавления записи
            cursor.execute("""
                INSERT INTO public.current_repair (cod_rep_work, inn_org, cod_num_hom, name_of_work, date_start, date_end)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cod_rep_work, inn_org, cod_num_hom, name_of_work, date_start, date_end))

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
        inn_org = self.table.item(selected_row, 1).text()
        cod_num_hom = self.table.item(selected_row, 2).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить запись с кодом работы {cod_rep_work}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute(
                    "DELETE FROM public.current_repair WHERE cod_rep_work = %s AND inn_org = %s AND cod_num_hom = %s",
                    (cod_rep_work, inn_org, cod_num_hom))
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
        inn_org = self.table.item(selected_row, 1).text()
        cod_num_hom = self.table.item(selected_row, 2).text()
        name_of_work = self.table.item(selected_row, 3).text()
        date_start = self.table.item(selected_row, 4).text()
        date_end = self.table.item(selected_row, 5).text()

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

        lbl_inn_org = QLabel("ИНН организации:")
        edit_inn_org = QLineEdit(inn_org)
        edit_inn_org.setReadOnly(True)
        layout.addWidget(lbl_inn_org)
        layout.addWidget(edit_inn_org)

        lbl_cod_num_hom = QLabel("Код номера дома:")
        edit_cod_num_hom = QLineEdit(cod_num_hom)
        edit_cod_num_hom.setReadOnly(True)
        layout.addWidget(lbl_cod_num_hom)
        layout.addWidget(edit_cod_num_hom)

        lbl_name_of_work = QLabel("Наименование работы:")
        edit_name_of_work = QLineEdit(name_of_work)
        layout.addWidget(lbl_name_of_work)
        layout.addWidget(edit_name_of_work)

        lbl_date_start = QLabel("Дата начала:")
        edit_date_start = QLineEdit(date_start)
        layout.addWidget(lbl_date_start)
        layout.addWidget(edit_date_start)

        lbl_date_end = QLabel("Дата окончания:")
        edit_date_end = QLineEdit(date_end)
        layout.addWidget(lbl_date_end)
        layout.addWidget(edit_date_end)

        # Кнопка для изменения записи
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.update_record(
            cod_rep_work,
            edit_inn_org.text(),
            edit_cod_num_hom.text(),
            edit_name_of_work.text(),
            edit_date_start.text(),
            edit_date_end.text(),
            dialog
        ))
        layout.addWidget(btn_edit)

        dialog.setLayout(layout)
        dialog.exec()

    def update_record(self, cod_rep_work, inn_org, cod_num_hom, name_of_work, date_start, date_end, dialog):
        if is_empty(name_of_work):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы не может быть пустым.')
            return
        if not contains_only_cor_text(name_of_work):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы содержит некорректные символы.')
            return
        if not has_correct_length(name_of_work, 50):
            QMessageBox.warning(self, 'Ошибка', 'Наименование работы должен быть длиной не более 50 символов.')

        if is_empty(date_start):
            QMessageBox.warning(self, 'Ошибка', 'Не введен дата начала ремонтных работ.')
            return
        if not is_cor_date(date_start):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата начала ремонтных работ.')
            return

        if is_empty(date_end):
            QMessageBox.warning(self, 'Ошибка', 'Не введен дата окончания ремонтных работ.')
            return
        if not is_cor_date(date_end):
            QMessageBox.warning(self, 'Ошибка', 'Некорректная дата окончания ремонтных работ.')
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Выполняем SQL-запрос для изменения записи
            cursor.execute("""
                UPDATE public.current_repair
                SET  name_of_work = %s, date_start = %s, date_end = %s
                WHERE cod_rep_work = %s AND inn_org = %s AND cod_num_hom = %s
            """, (name_of_work, date_start, date_end, cod_rep_work, inn_org, cod_num_hom))

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
