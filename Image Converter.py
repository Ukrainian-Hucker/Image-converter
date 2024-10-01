import sys
import os
import zipfile
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget, QMessageBox, QLabel, QComboBox, QCheckBox, QAbstractItemView, QDialog, QDialogButtonBox, QFrame)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PIL import Image
import qdarkstyle
import darkdetect
import json

class Translator:
    def __init__(self, lang_code):
        self.translations = {}
        self.load_translations(lang_code)

    def load_translations(self, lang_code):
        file_path = os.path.join('_internal\locales', f'{lang_code}.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            self.translations = json.load(file)

    def translate(self, text):
        return self.translations.get(text, text)

class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.translator = Translator('en')  # Задаємо мову за замовчуванням
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.translator.translate('Image Converter'))
        self.setGeometry(543, 450, 600, 581)
        
        main_layout = QVBoxLayout()
        
        title_layout = QHBoxLayout()
        
        self.titleLabel = QLabel(self.translator.translate("Image Converter"))
        self.titleLabel.setFont(QFont('Sitka Banner', 25))
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.settingsButton = QPushButton('', self)
        self.settingsButton.setIcon(QIcon('_internal/icons/ico.png'))
        self.settingsButton.setIconSize(QSize(25, 25))
        self.settingsButton.setToolTip(self.translator.translate('Settings'))
        self.settingsButton.setFixedSize(30, 30)
        self.settingsButton.clicked.connect(self.open_settings)

        title_layout.addWidget(self.titleLabel)
        title_layout.addWidget(self.settingsButton, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(title_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line1)

        self.fileList = QListWidget(self)
        self.fileList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        main_layout.addWidget(self.fileList)
        self.fileList.setMaximumHeight(250)

        self.uploadButton = QPushButton(self.translator.translate('Upload Files'), self)
        self.uploadButton.setFont(QFont('Arial', 12))
        self.uploadButton.setIcon(QIcon('_internal/icons/Upload.png'))
        self.uploadButton.clicked.connect(self.upload_files)
        main_layout.addWidget(self.uploadButton)
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line2)
        
        self.formatLabel = QLabel(self.translator.translate("Select Output Format:"))
        self.formatLabel.setFont(QFont('Arial', 15))
        self.formatLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.formatLabel)
        
        self.formatComboBox = QComboBox(self)
        self.formatComboBox.setFont(QFont('Arial', 12))
        self.formatComboBox.addItems(['PNG', 'JPG', 'ICO', 'BMP'])
        main_layout.addWidget(self.formatComboBox)

        self.zipCheckBox = QCheckBox(self.translator.translate('Save all converted files in a ZIP archive'))
        self.zipCheckBox.setFont(QFont('Arial', 14))
        main_layout.addWidget(self.zipCheckBox)

        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line3)
        
        self.convertButton = QPushButton(self.translator.translate('Convert'), self)
        self.convertButton.setFont(QFont('Arial', 14))
        self.convertButton.setIcon(QIcon('_internal/icons/setting.ico'))
        self.convertButton.clicked.connect(self.convert_images)
        main_layout.addWidget(self.convertButton)
        
        self.setLayout(main_layout)

    def open_settings(self):
        settings_window = SettingsWindow(self.translator)
        settings_window.themeChanged.connect(self.change_theme)
        settings_window.languageChanged.connect(self.change_language)
        settings_window.exec()

    def change_theme(self, theme):
        if theme == 'Light':
            app.setStyleSheet('')
            self.translator.translate
        elif theme == 'Dark':
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
            self.translator.translate
        elif theme == 'System':
            self.apply_system_theme()

    def apply_system_theme(self):
        if darkdetect.isDark():
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        else:
            app.setStyleSheet('')

    def change_language(self, language):
        if language == 'Українська':
            self.translator = Translator('uk')
        else:
            self.translator = Translator('en')
        self.initUI()

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.translator.translate("Select Images"), "", "Images (*.png *.jpg *.ico *.bmp *.webp)")
        if files:
            for file in files:
                self.fileList.addItem(file)

    def convert_images(self):
        items = self.fileList.selectedItems()
        if not items:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("No files selected for conversion"))
            return

        format_choice = self.formatComboBox.currentText()
        if not format_choice:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("No output format selected"))
            return

        save_as_zip = self.zipCheckBox.isChecked()
        if save_as_zip:
            zip_path = QFileDialog.getSaveFileName(self, self.translator.translate("Save ZIP Archive"), "", self.translator.translate("ZIP files (*.zip)"))[0]
            if not zip_path:
                return

        converted_files = []
        for item in items:
            input_path = item.text()
            try:
                img = Image.open(input_path)
                if save_as_zip:
                    output_path = os.path.join(os.path.dirname(zip_path), os.path.splitext(os.path.basename(input_path))[0] + f".{format_choice.lower()}")
                    converted_files.append((img, output_path))
                else:
                    output_path = QFileDialog.getSaveFileName(self, self.translator.translate("Save Converted Image"), "", f"{format_choice} files (*.{format_choice.lower()})")[0]
                    if output_path:
                        img.save(output_path, format=format_choice.upper())
                        QMessageBox.information(self, self.translator.translate("Success"), f"{self.translator.translate('Image saved successfully as')} {output_path}")
            except Exception as e:
                QMessageBox.critical(self, self.translator.translate("Error"), f"{self.translator.translate('Failed to convert image:')} {e}")

        if save_as_zip and converted_files:
            try:
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for img, path in converted_files:
                        img.save(path, format=format_choice.upper())
                        zipf.write(path, os.path.basename(path))
                        os.remove(path)
                QMessageBox.information(self, self.translator.translate("Success"), f"{self.translator.translate('All files saved successfully in')} {zip_path}")
            except Exception as e:
                QMessageBox.critical(self, self.translator.translate("Error"), f"{self.translator.translate('Failed to create ZIP archive:')} {e}")

class SettingsWindow(QDialog):
    themeChanged = pyqtSignal(str)
    languageChanged = pyqtSignal(str)

    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.translator.translate('Settings'))
        self.setGeometry(400, 300, 300, 200)
        
        layout = QVBoxLayout()
        
        self.languageLabel = QLabel(self.translator.translate("Select Language:"))
        self.languageLabel.setFont(QFont('Arial', 14))
        layout.addWidget(self.languageLabel)
        
        self.languageComboBox = QComboBox(self)
        self.languageComboBox.setFont(QFont('Arial', 12))
        self.languageComboBox.addItems(['English', 'Українська'])
        layout.addWidget(self.languageComboBox)

        self.themeLabel = QLabel(self.translator.translate("Select Theme:"))
        self.themeLabel.setFont(QFont('Arial', 14))
        layout.addWidget(self.themeLabel)
        
        self.themeComboBox = QComboBox(self)
        self.themeComboBox.setFont(QFont('Arial', 12))
        self.themeComboBox.addItems(['Dark', 'Light', 'System'])
        self.themeComboBox.setCurrentText('System')
        layout.addWidget(self.themeComboBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_changes)
        buttonBox.accepted.connect(self.apply_changes)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def apply_changes(self):
        selected_theme = self.themeComboBox.currentText()
        self.themeChanged.emit(selected_theme)

        selected_language = self.languageComboBox.currentText()
        self.languageChanged.emit(selected_language)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    if darkdetect.isDark():
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    else:
        app.setStyleSheet('')

    ex = ImageConverter()
    ex.show()
    sys.exit(app.exec())