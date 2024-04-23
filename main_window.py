import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from apartment_window import ApartmentWindow  # Здесь подключаем окна для каждой таблицы
from flat_window import FlatWindow
from owner_window import OwnerWindow
from builder_window import BuilderWindow
from repair_work_window import RepairWorkWindow
from current_repair_window import CurrentRepairWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление базой данных регионального оператора капитального ремонта")
        self.initUI()
        self.resize(1280, 720)

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Кнопка для переключения на окно работы с таблицей apartment
        btn_apartment = QPushButton("Таблица многоквартирных домов")
        btn_apartment.clicked.connect(self.show_apartment_window)
        layout.addWidget(btn_apartment)

        btn_flat = QPushButton("Таблица квартир")
        btn_flat.clicked.connect(self.show_flat_window)
        layout.addWidget(btn_flat)

        btn_owner = QPushButton("Таблица владельцев квартир")
        btn_owner.clicked.connect(self.show_owner_window)
        layout.addWidget(btn_owner)

        btn_bldr = QPushButton("Таблица строительных организаций")
        btn_bldr.clicked.connect(self.show_builder_window)
        layout.addWidget(btn_bldr)

        btn_repair_work = QPushButton("Таблица ремонтных работ")
        btn_repair_work.clicked.connect(self.show_repair_work_window)
        layout.addWidget(btn_repair_work)

        btn_current_repair = QPushButton("Таблица текущих ремонтных работ")
        btn_current_repair.clicked.connect(self.show_current_repair_window)
        layout.addWidget(btn_current_repair)

        self.central_widget.setLayout(layout)

    def show_apartment_window(self):
        self.apartment_window = ApartmentWindow()
        self.apartment_window.show()

    def show_flat_window(self):
        self.flat_window = FlatWindow()
        self.flat_window.show()

    def show_owner_window(self):
        self.owner_window = OwnerWindow()
        self.owner_window.show()

    def show_builder_window(self):
        self.builder_window = BuilderWindow()
        self.builder_window.show()

    def show_repair_work_window(self):
        self.repair_work_window = RepairWorkWindow()
        self.repair_work_window.show()

    def show_current_repair_window(self):
        self.current_repair_work_window = CurrentRepairWindow()
        self.current_repair_work_window.show()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
