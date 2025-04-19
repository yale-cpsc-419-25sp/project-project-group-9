#home.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QStackedWidget, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt
import sys
import socket
import pickle
import requests

class HomeClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def query_server(self, page):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                data = pickle.dumps(page)
                sock.sendall(data)
                sock.shutdown(socket.SHUT_WR)
                response = sock.recv(4096)
                return pickle.loads(response)
        except Exception as e:
            return f"Error: {e}"

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = HomeClient()
        self.setWindowTitle("Lux Navigation Bar")
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.pages = {
            "Mentor Listings": QLabel("Welcome to Mentor Listings"),
            "Community Pages": QLabel("Explore Community Pages"),
            "Profile": QLabel("View Your Profile"),
            "Take the Quiz!": self.create_login_page()
        }

        for page in self.pages.values():
            if isinstance(page, QLabel):
                page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(page)

        nav_bar = self.create_nav_bar()
        main_layout = QVBoxLayout()
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stack)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Check CAS authentication on launch
        self.check_login_status()

    def create_nav_bar(self):
        nav_bar = QFrame()
        nav_bar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                padding: 10px;
                border-bottom: 2px solid #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(10)
        for page_name in self.pages.keys():
            button = QPushButton(page_name.title())
            button.clicked.connect(lambda checked=False, name=page_name: self.navigate_to(name))
            nav_layout.addWidget(button)
        nav_bar.setLayout(nav_layout)
        return nav_bar

    def create_login_page(self):
        login_widget = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("Not logged in")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_button = QPushButton("Login with Yale CAS")
        login_button.clicked.connect(self.cas_login)

        layout.addWidget(self.status_label)
        layout.addWidget(login_button)
        login_widget.setLayout(layout)

        return login_widget

    def cas_login(self):
        """Redirect user to CAS login."""
        requests.get("http://localhost:5000/login")  # Calls CAS authentication on your Flask server.
        self.check_login_status()

    def check_login_status(self):
        """Check if the user is authenticated via CAS."""
        try:
            response = requests.get("http://localhost:5000/user").text
            self.status_label.setText(response)
        except requests.exceptions.RequestException:
            self.status_label.setText("Error connecting to authentication server")

    def navigate_to(self, page_name):
        page = self.pages.get(page_name)
        if page:
            self.stack.setCurrentWidget(page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
