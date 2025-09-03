import sys
import os
import tempfile
import uuid
import qrcode
import barcode
from barcode.writer import ImageWriter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QComboBox, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas
import qtawesome as qta  # <<< novo


class CodeGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Código de Barras & QR Code")
        self.setWindowIcon(qta.icon("mdi6.qrcode-scan", color="blue"))  # ícone janela
        self.setMinimumSize(800, 500)
        self.temp_file = None
        self.current_theme = "dark"  # tema inicial
        self.initUI()
        self.apply_styles(self.current_theme)

    def initUI(self):
        # Layout principal vertical
        main_vertical = QVBoxLayout()

        # Label título
        self.title_label = QLabel("Gerador de Códigos QR/Barcode")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")

        main_vertical.addWidget(self.title_label)

        # Layout horizontal para conteúdo
        main_layout = QHBoxLayout()

        # Painel esquerdo (controles)
        layout = QVBoxLayout()

        self.input_label = QLabel("Introduza Texto / URL / Número:")
        self.input_field = QTextEdit()
        self.input_field.setAcceptRichText(False)
        self.input_field.setLineWrapMode(QTextEdit.WidgetWidth)
        self.input_field.setPlaceholderText("Cole aqui o seu texto ou URL longo...")
        self.input_field.setFixedHeight(120)

        self.type_label = QLabel("Selecione o Tipo de Código:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["QR Code", "EAN13", "Code128"])
        self.type_combo.setMinimumHeight(40)

        self.generate_btn = QPushButton(" Gerar")
        self.generate_btn.setIcon(qta.icon("fa6s.wand-magic", color="white"))  # ícone gerar
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.clicked.connect(self.generate_code)

        self.save_btn = QPushButton(" Guardar como Imagem/PDF")
        self.save_btn.setIcon(qta.icon("fa5.save", color="white"))  # ícone guardar
        self.save_btn.setMinimumHeight(50)
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)

        # Botão alternar tema
        self.theme_btn = QPushButton(" Alternar Tema")
        self.theme_btn.setIcon(qta.icon("ei.adjust-alt", color="white"))  # ícone tema
        self.theme_btn.setMinimumHeight(40)
        self.theme_btn.clicked.connect(self.toggle_theme)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.theme_btn)
        layout.addStretch()

        # Painel direito (preview)
        self.image_label = QLabel("O seu código aparecerá aqui")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(True)
        self.image_label.setStyleSheet("border: 2px dashed #555; padding: 20px; font-size: 18px;")

        main_layout.addLayout(layout, 1)
        main_layout.addWidget(self.image_label, 2)

        # Adiciona o título + main_layout
        main_vertical.addLayout(main_layout)
        self.setLayout(main_vertical)

    def apply_styles(self, theme="dark"):
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial;
                    font-size: 16px;
                    background-color: #1e1e2f;
                    color: #f0f0f0;
                }
                QLabel {
                    font-size: 18px;
                }
                QTextEdit, QComboBox {
                    background-color: #2b2b3d;
                    color: #f0f0f0;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #2e86de;
                    color: white;
                    padding: 12px;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1b4f72;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #aaa;
                }
                QComboBox QAbstractItemView {
                    background-color: #2b2b3d;
                    selection-background-color: #2e86de;
                    selection-color: white;
                    font-size: 16px;
                }
            """)
            self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f0f0f0; margin-bottom: 15px;")
        elif theme == "light":
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial;
                    font-size: 16px;
                    background-color: #f5f5f5;
                    color: #1e1e1e;
                }
                QLabel {
                    font-size: 18px;
                }
                QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #1e1e1e;
                    border: 1px solid #bbb;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    padding: 12px;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                    color: #666;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    selection-background-color: #0078d7;
                    selection-color: white;
                    font-size: 16px;
                }
            """)
            self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e1e1e; margin-bottom: 15px;")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_styles(self.current_theme)

    def generate_code(self):
        text = self.input_field.toPlainText().strip()
        code_type = self.type_combo.currentText()

        if not text:
            QMessageBox.warning(self, "Erro de Entrada", "Por favor introduza algum texto ou número.")
            return

        try:
            unique_name = str(uuid.uuid4()) + ".png"
            temp_dir = tempfile.gettempdir()
            self.temp_file = os.path.join(temp_dir, unique_name)

            if code_type == "QR Code":
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(self.temp_file)
            else:
                if code_type == "EAN13" and (not text.isdigit() or len(text) != 12):
                    QMessageBox.warning(self, "Erro de Entrada", "EAN13 requer exatamente 12 dígitos.")
                    return
                barcode_class = barcode.get_barcode_class(code_type.lower())
                bar = barcode_class(text, writer=ImageWriter())
                bar.save(self.temp_file[:-4])
                self.temp_file = self.temp_file[:-4] + ".png"

            pixmap = QPixmap(self.temp_file)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            self.save_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def save_file(self):
        if not self.temp_file or not os.path.exists(self.temp_file):
            QMessageBox.warning(self, "Erro", "Nenhum código gerado para guardar.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Guardar Ficheiro", "",
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
