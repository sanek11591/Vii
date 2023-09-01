from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon


class SettingsWindow(QMainWindow):
    data_of_select_model = pyqtSignal(str)
    data_of_select_cpu_gpu = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 150)
        self.setWindowTitle("Настройки")
        layout = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout2.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setLayout(layout)
        self.button_group_gpu_cpu = QButtonGroup(self)
        self.button_group_model = QButtonGroup(self)
        self.label = QLabel("Выбор модели", self)
        layout.addWidget(self.label)
        self.label_cuda = QLabel("На чем обрабатывать")
        layout2.addWidget(self.label_cuda)

        self.radio_cpu = QRadioButton("CPU", self)
        self.radio_cpu.setChecked(True)  # Включаем первый переключатель по умолчанию
        self.radio_cpu.toggled.connect(self.show_rb_o)
        self.button_group_gpu_cpu.addButton(self.radio_cpu)
        layout2.addWidget(self.radio_cpu)

        self.radio_gpu = QRadioButton("GPU", self)
        self.radio_gpu.toggled.connect(self.show_rb_o)
        self.button_group_gpu_cpu.addButton(self.radio_gpu)
        layout2.addWidget(self.radio_gpu)

        self.radio_large = QRadioButton("Большая", self)
        self.radio_large.setChecked(True)  # Включаем первый переключатель по умолчанию
        self.radio_large.toggled.connect(self.show_rb_status)
        self.button_group_model.addButton(self.radio_large)
        layout.addWidget(self.radio_large)

        self.radio_medium = QRadioButton("Средняя", self)
        self.radio_medium.toggled.connect(self.show_rb_status)
        self.button_group_model.addButton(self.radio_medium)
        layout.addWidget(self.radio_medium)

        self.radio_small = QRadioButton("Маленькая", self)
        self.radio_small.toggled.connect(self.show_rb_status)
        self.button_group_model.addButton(self.radio_small)
        layout.addWidget(self.radio_small)
        main_layout.addLayout(layout)
        main_layout.addLayout(layout2)
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def show_rb_status(self):
        rb = self.sender()
        if rb.isChecked():
            self.data_of_select_model.emit(rb.text())

    def show_rb_o(self):
        rb = self.sender()
        if rb.isChecked():
            self.data_of_select_cpu_gpu.emit(rb.text())

