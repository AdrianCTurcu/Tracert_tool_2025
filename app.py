import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import ctypes
import sys

if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class TracertThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, address):
        super().__init__()
        self.address = address
        self.process = None

    def run(self):
        self.process = subprocess.Popen(
            ["tracert", self.address],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in iter(self.process.stdout.readline, ''):
            self.output_signal.emit(line.strip())
        self.process.stdout.close()
        self.process.wait()

    def stop(self):
        if self.process:
            self.process.terminate()

class TracertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tracert app by Adrian T")
        self.setGeometry(300, 200, 600, 750)
        self.setFixedSize(self.size())
        

        # Background olive
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(204, 230, 204))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Address Label
        self.label_address = QLabel("Address:")
        self.label_address.setFont(QFont("Times New Roman", 12, QFont.Bold))
        layout.addWidget(self.label_address)

        # Input URL
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Your search IP address here..")
        self.input_url.setFont(QFont("Times New Roman", 12))
        self.input_url.returnPressed.connect(self.run_tracert)
        layout.addWidget(self.input_url)

        # Start + Stop buttons in same row
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Start Tracert")
        self.check_button.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.check_button.setFixedWidth(200)
        self.check_button.setStyleSheet("padding: 8px;")
        self.check_button.clicked.connect(self.run_tracert)
        button_layout.addWidget(self.check_button, alignment=Qt.AlignCenter)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.stop_button.setFixedWidth(100)
        self.stop_button.setStyleSheet("padding: 8px; background-color: #ff9999;")
        self.stop_button.clicked.connect(self.stop_tracert)
        button_layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)

        layout.addLayout(button_layout)

        # Result area
        self.result_area = QTextEdit()
        self.result_area.setFont(QFont("Courier New", 10))
        self.result_area.setReadOnly(True)
        self.result_area.setMinimumHeight(300)
        layout.addWidget(self.result_area)

        # Copyright
        self.copy_label = QLabel("© Adrian T")
        self.copy_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.copy_label.setFont(QFont("Times New Roman", 10, QFont.Bold))
        layout.addWidget(self.copy_label)

        self.setLayout(layout)
        self.thread = None

    def run_tracert(self):
        address = self.input_url.text().strip()
        if not address:
            self.result_area.setText("⚠ Introdu o adresă!")
            return

        self.result_area.clear()
        self.input_url.clear()
        self.thread = TracertThread(address)
        self.thread.output_signal.connect(self.append_output)
        self.thread.start()

    def stop_tracert(self):
        if self.thread:
            self.thread.stop()
            self.result_area.append('<span style="color:red; font-weight:bold;">⛔ Tracert oprit de utilizator.</span>')

    def append_output(self, text):
        if "Tracing route to" in text:
            # Extragem domeniul și IP-ul
            try:
                domain = text.split("Tracing route to ")[1].split(" [")[0]
                ip_address = text.split("[")[1].split("]")[0]
            except:
                domain = ""
                ip_address = ""

            # Construim linia colorată
            colored_line = (
                f'Tracing route to '
                f'<span style="color:green; font-weight:bold;">{domain}</span> '
                f'[<span style="color:red; font-weight:bold;">{ip_address}</span>]'
            )

            self.result_area.append(colored_line)
        elif "Trace complete" in text:
                self.result_area.append('<span style="color:green; font-weight:bold;">Trace complete.</span>')

        else:
                self.result_area.append(text)

        self.result_area.moveCursor(self.result_area.textCursor().End)

    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TracertApp()
    window.show()
    sys.exit(app.exec_())
