"""
Main file for launching the Water Tracker application.
"""

import ttkbootstrap as ttk
from ui.main_window import MainWindow


def main():
    """Launches the main application window."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
