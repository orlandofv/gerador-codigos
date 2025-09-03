import sys
import os
import tempfile
import uuid
import qrcode
import barcode
from barcode.writer import ImageWriter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QComboBox, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas

class CodeGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Código de Barras & QR Code")
        self.setMinimumSize(500, 400)
        self.temp_file = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input field
        self.input_label = QLabel("Introduza Texto / Número:")
        self.input_field = QLineEdit()

        # Dropdown for type selection
        self.type_label = QLabel("Selecione o Tipo de Código:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["QR Code", "EAN13", "Code128"])

        # Generate button
        self.generate_btn = QPushButton("Gerar")
        self.generate_btn.clicked.connect(self.generate_code)

        # Image preview
        self.image_label = QLabel("O seu código aparecerá aqui")
        self.image_label.setAlignment(Qt.AlignCenter)

        # Save button
        self.save_btn = QPushButton("Guardar como Imagem/PDF")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)

        # Layout setup
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.save_btn)
        layout.addStretch()
        
        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.image_label)
        
        self.setLayout(main_layout)

    def generate_code(self):
        text = self.input_field.text().strip()
        code_type = self.type_combo.currentText()

        if not text:
            QMessageBox.warning(self, "Erro de Entrada", "Por favor introduza algum texto ou número.")
            return

        try:
            # Unique file name in OS temp folder
            unique_name = str(uuid.uuid4()) + ".png"
            temp_dir = tempfile.gettempdir()
            self.temp_file = os.path.join(temp_dir, unique_name)

            if code_type == "QR Code":
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(self.temp_file)

            else:  # Barcode
                if code_type == "EAN13" and (not text.isdigit() or len(text) != 12):
                    QMessageBox.warning(self, "Erro de Entrada", "EAN13 requer exatamente 12 dígitos.")
                    return
                barcode_class = barcode.get_barcode_class(code_type.lower())
                bar = barcode_class(text, writer=ImageWriter())
                bar.save(self.temp_file[:-4])  # barcode lib auto adds .png
                self.temp_file = self.temp_file[:-4] + ".png"

            # Display image
            pixmap = QPixmap(self.temp_file)
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
            self.save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def save_file(self):
        if not self.temp_file or not os.path.exists(self.temp_file):
            QMessageBox.warning(self, "Erro", "Nenhum código gerado para guardar.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Guardar Ficheiro",
            "",
            "PNG (*.png);;JPG (*.jpg);;PDF (*.pdf)"
        )

        if file_path:
            try:
                if selected_filter == "PDF (*.pdf)":
                    c = canvas.Canvas(file_path)
                    c.drawImage(self.temp_file, 50, 600, 300, 300)
                    c.save()
                else:
                    pixmap = self.image_label.pixmap()
                    if pixmap:
                        pixmap.save(file_path)
                QMessageBox.information(self, "Guardado", f"Ficheiro guardado em {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeGeneratorApp()
    window.show()
    sys.exit(app.exec_())
