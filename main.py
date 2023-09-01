import sys
import os
import pathlib
import obrabotka_vad
import obrabotka_whisper
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import setting_window
import torch
import file_list_window
from PyQt6.QtGui import QIcon
import time


class Worker(QThread):
    error_occurred = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._mutex = QMutex()

    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    warnings = pyqtSignal(str)
    complete_massage = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_list_windows = None
        self.settings_window = None
        self.model_size_settings = "large"
        self.cpu_gpu_settings = "cpu"
        self.start_timer = None
        self.list_of_files_path_for_processing_whisper = []
        self.list_of_files_path_for_processing_vad = []
        self.statusList = []
        self.setWindowTitle("Вий")
        self.setWindowIcon(QIcon('icon.jpg'))
        self.label_for_select_dir = QLabel()
        self.label_for_select_dir.setFixedSize(300, 20)
        self.label_for_select_dir.setStyleSheet("border-style: solid;"
                                                "border-width: 1px;"
                                                "border-color: black;")
        self.label_for_select_dir.setText("Выберите папку c аудио файлами")

        self.button_for_select_dir = QPushButton()
        self.button_for_select_dir.setText("Выбрать")

        self.label_for_select_dir_save = QLabel()
        self.label_for_select_dir_save.setFixedSize(300, 20)
        self.label_for_select_dir_save.setStyleSheet("border-style: solid;"
                                                     "border-width: 1px;"
                                                     "border-color: black;")
        self.label_for_select_dir_save.setText("Выберите папку куда сохранить файлы")

        self.button_for_select_dir_save = QPushButton()
        self.button_for_select_dir_save.setText("Выбрать")

        self.label_for_status = QLabel()
        self.label_for_status.setMinimumSize(400, 300)
        self.label_for_status.setStyleSheet(
            f"qproperty-alignment: {int(Qt.AlignmentFlag.AlignHCenter & Qt.AlignmentFlag.AlignLeft)};")
        self.label_for_status.setWordWrap(True)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label_for_status)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.label_for_status_title = QLabel()
        self.label_for_status_title.setText("Статус")
        self.label_for_status_title.setStyleSheet(f"qproperty-alignment: {int(Qt.AlignmentFlag.AlignHCenter)};")

        self.button_for_start_processing = QPushButton()
        self.button_for_start_processing.setText("Начать обработку")

        self.button_for_exit = QPushButton()
        self.button_for_exit.setText("Выход")

        self.settings_button = QPushButton()
        self.settings_button.setText("Настройки")

        self.cuda_status = QLabel()
        self.cuda_status.setStyleSheet("border-style: solid;"
                                       "border-width: 1px;"
                                       "border-color: black;")
        self.cuda_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if torch.cuda.is_available():
            self.cuda_status.setText("Доступен GPU")
            self.cuda_status.setStyleSheet("background-color: green;")
        else:
            self.cuda_status.setText("Не доступен GPU")
            self.cuda_status.setStyleSheet("background-color: red;")

        layout_of_status = QHBoxLayout()
        layout_of_status.addWidget(self.cuda_status)
        layout_of_status.addWidget(self.label_for_status_title)
        layout_of_status.addWidget(self.settings_button)

        layout_of_select_dir = QHBoxLayout()
        layout_of_select_dir.addWidget(self.label_for_select_dir)
        layout_of_select_dir.addWidget(self.button_for_select_dir)

        layout_of_select_dir_for_save = QHBoxLayout()
        layout_of_select_dir_for_save.addWidget(self.label_for_select_dir_save)
        layout_of_select_dir_for_save.addWidget(self.button_for_select_dir_save)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_of_select_dir)
        main_layout.addLayout(layout_of_select_dir_for_save)
        main_layout.addWidget(self.button_for_start_processing)
        main_layout.addLayout(layout_of_status)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.button_for_exit)

        container = QWidget()
        container.setLayout(main_layout)
        self.setFixedSize(500, 500)
        self.setCentralWidget(container)
        self.button_for_select_dir.clicked.connect(self.select_directory_button)
        self.button_for_select_dir_save.clicked.connect(self.select_directory_button_for_save)
        self.button_for_start_processing.clicked.connect(
            lambda: self.start(self.label_for_select_dir_save.text(), self.label_for_select_dir.text()))
        self.button_for_exit.clicked.connect(QApplication.instance().quit)
        self.settings_button.clicked.connect(self.settings)
        self.worker = None
        self.mutex = QMutex()
        self.warnings.connect(self.warning)
        self.complete_massage.connect(self.complete)

    def update_status_list(self, new_status):
        self.mutex.lock()
        try:
            self.statusList.append(new_status)
        finally:
            self.mutex.unlock()

    def select_directory_button(self):
        directory = str(QFileDialog().getExistingDirectory())
        self.label_for_select_dir.setText(os.path.normpath(directory))
        #self.file_list_window(directory)

    def select_directory_button_for_save(self):
        directory = str(QFileDialog().getExistingDirectory())
        self.label_for_select_dir_save.setText(os.path.normpath(directory))

    def start(self, directory_to_save, directory_to_process):
        self.worker = Worker(self.start_processing_vad, directory_to_save, directory_to_process)
        self.worker.error_occurred.connect(self.error)
        self.worker.start()

    def start_processing_vad(self, label_for_select_dir_save, label_for_select_dir):

        current_directory_for_processing_files_vad = pathlib.Path(label_for_select_dir)
        directory_for_save_files = pathlib.Path(label_for_select_dir_save)
        current_patterns = ["*.wav", "*.mp3", "*.ogg", "*.m4a"]
        for current_pattern in current_patterns:
            for currentFile in current_directory_for_processing_files_vad.glob(current_pattern):
                self.list_of_files_path_for_processing_vad.append(currentFile.absolute())
        if not self.list_of_files_path_for_processing_vad:
            self.warnings.emit("Директория с файлами пуста или нет аудио файлов")
            return 0
        if not directory_for_save_files.exists() or str(directory_for_save_files) == '.':
            self.warnings.emit("Директория для сохранения не существует")
            return 0

        else:
            if directory_for_save_files == current_directory_for_processing_files_vad:
                p = pathlib.Path(str(pathlib.PurePath(directory_for_save_files)) + "\\obrabotka")
                p.mkdir(parents=True, exist_ok=True)
                directory_for_save_files = pathlib.Path(
                    str(pathlib.PurePath(directory_for_save_files)) + "\\obrabotka")
                label_for_select_dir_save = pathlib.Path(
                    str(pathlib.PurePath(directory_for_save_files)))
            for audio_file_path in self.list_of_files_path_for_processing_vad:
                self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
                self.update_status_list(f"Начата обработка VAD файла {audio_file_path.name}.")
                self.label_for_status.setText('\n'.join(self.statusList))
                self.start_timer = time.time()
                status, ok_or_on = obrabotka_vad.VAD.selerio_vad(audio_file_path, directory_for_save_files.absolute())
                if ok_or_on:
                    self.update_status_list(status)
                    self.label_for_status.setText('\n'.join(self.statusList))
                else:
                    raise Exception(status)
                self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
            self.start_processing_whisper(label_for_select_dir_save)
            self.complete_massage.emit()

    def start_processing_whisper(self, label_for_select_dir_save):
        current_pattern = "*.wav"
        directory_for_save_files = pathlib.Path(label_for_select_dir_save)
        for currentFile in directory_for_save_files.glob(current_pattern):
            self.list_of_files_path_for_processing_whisper.append(currentFile.absolute())
        for audio_file_path in self.list_of_files_path_for_processing_whisper:
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
            self.update_status_list(f"Старт преобразования файла {audio_file_path.name} в текст.")
            self.label_for_status.setText('\n'.join(self.statusList))
            status, ok_or_on = obrabotka_whisper.Whisper.speach_to_text(audio_file_path.absolute(),
                                                                        self.model_size_settings, self.cpu_gpu_settings)
            if ok_or_on:
                self.update_status_list(status)
                self.update_status_list("Время обработки " + str(round(time.time() - self.start_timer)) + " секунд")
                self.label_for_status.setText('\n'.join(self.statusList))
            else:
                raise Exception(status)
            self.start_timer = time.time()
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def settings(self):
        if self.settings_window is None:
            self.settings_window = setting_window.SettingsWindow()
            self.settings_window.data_of_select_model.connect(self.receive_data_form_settings_model_size)
            self.settings_window.data_of_select_cpu_gpu.connect(self.receive_data_form_settings_cpu_gpu)
            self.settings_window.show()
        else:
            self.settings_window.show()

    def receive_data_form_settings_model_size(self, data):
        if data == "Большая":
            self.model_size_settings = "large-v2"
        elif data == "Средняя":
            self.model_size_settings = "medium"
        elif data == "Маленькая":
            self.model_size_settings = "base"

    def receive_data_form_settings_cpu_gpu(self, data):
        if data == "CPU":
            self.cpu_gpu_settings = "cpu"
        elif data == "GPU":
            self.cpu_gpu_settings = "cuda"

    def file_list_window(self, directory_to_process):
        self.file_list_windows = file_list_window.FileListWindow(directory_to_process)
        self.file_list_windows.show()

    @pyqtSlot(str)
    def error(self, e):
        QMessageBox.critical(None, "Ошибка", e, QMessageBox.StandardButton.Cancel)

    @pyqtSlot(str)
    def warning(self, w):
        QMessageBox.warning(None, "Предупреждение", w, QMessageBox.StandardButton.Ok)

    @pyqtSlot()
    def complete(self):
        complete_message = QMessageBox()
        complete_message.setWindowTitle("Выполнено")
        complete_message.setText("Все файлы успешно обработаны!")
        complete_message.setIcon(QMessageBox.Icon.Information)
        complete_message.setStandardButtons(QMessageBox.StandardButton.Ok)
        complete_message.exec()
 

app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec()
