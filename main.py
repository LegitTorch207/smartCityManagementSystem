from PyQt6.QtGui import QFont

from ui_login import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet("""
        QWidget {
        color: #1E293B;
        }
        QMainWindow, QWidget {
            background-color: #F8FAFC;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            margin-top: 8px;
            padding: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 4px;
            color: #334155;
        }
        QPushButton {
            padding: 6px 14px;
            border-radius: 4px;
            border: 1px solid #CBD5E1;
            background-color: #FFFFFF;
        }
        QPushButton:hover {
            background-color: #E2E8F0;
        }
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: #FFFFFF;
        }
        QTableWidget {
            border: 1px solid #CBD5E1;
            background-color: #FFFFFF;
            gridline-color: #E2E8F0;
        }
        QHeaderView::section {
            background-color: #F1F5F9;
            padding: 6px;
            border: none;
            font-weight: bold;
            color: #475569;
        }
        QTabWidget::pane {
            border: 1px solid #CBD5E1;
        }
        QTabBar::tab {
            padding: 6px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2563EB;
            color: white;
            border-radius: 4px 4px 0 0;
        }
    """)

    # Open the login window
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()