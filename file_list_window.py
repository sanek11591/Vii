from PyQt6.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
import pathlib
from PyQt6.QtGui import QIcon


class FileListWindow(QMainWindow):

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.resize(350, 300)
        self.setWindowTitle("Список выбранных файлов")
        self.setWindowIcon(QIcon('icon.jpg'))
        self.file_list = []
        layout = QVBoxLayout()
        self.file_list_widget = QListWidget()
        layout.addWidget(self.file_list_widget)
        directory_for_save_files = pathlib.Path(self.directory)
        current_patterns = ["*.wav", "*.mp3", "*.ogg", "*.m4a"]
        for current_pattern in current_patterns:
            for currentFile in directory_for_save_files.glob(current_pattern):
                self.file_list.append(currentFile.name)
        for file_name in self.file_list:
            item = QListWidgetItem(str(file_name))
            self.file_list_widget.addItem(item)

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)
