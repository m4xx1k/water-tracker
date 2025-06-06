"""
Головний файл для запуску програми Water Tracker.
"""

import ttkbootstrap as ttk
from ui.main_window import MainWindow


def main():
    """Запускає головне вікно програми."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
