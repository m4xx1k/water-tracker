"""
Головне вікно програми.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.profile_frame import ProfileFrame
from ui.dashboard_frame import DashboardFrame
from ui.history_frame import HistoryFrame
from repository.data_store import DataStore
from services.profile_service import ProfileService
from services.water_log_service import WaterLogService


class MainWindow(ttk.Window):
    """Головне вікно програми."""
    
    def __init__(self):
        """Ініціалізує головне вікно програми."""
        super().__init__(title="Water Tracker", themename="cosmo", resizable=(False, False))
        
        # Ініціалізація сервісів
        self.data_store = DataStore()
        self.profile_service = ProfileService(self.data_store)
        self.water_log_service = WaterLogService(self.data_store, self.profile_service)
        
        # Налаштування вікна
        self.geometry("800x600")
        self.position_center()
        
        # Створення меню
        self.create_menu()
        
        # Основний контейнер
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Створення фреймів
        self.create_frames()
        
        # Встановлення початкового стану інтерфейсу
        self.check_profile()
    
    def create_menu(self):
        """Створює головне меню програми."""
        menu_bar = tk.Menu(self)
        
        # Меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Data...", command=self.export_data)
        file_menu.add_command(label="Import Data...", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Меню "Профіль"
        profile_menu = tk.Menu(menu_bar, tearoff=0)
        profile_menu.add_command(label="Create/Edit Profile", command=self.show_profile_frame)
        menu_bar.add_cascade(label="Profile", menu=profile_menu)
        
        # Меню "Вигляд"
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Dashboard", command=self.show_dashboard_frame)
        view_menu.add_command(label="History", command=self.show_history_frame)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Меню "Довідка"
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
    
    def create_frames(self):
        """Створює основні фрейми програми."""
        # Фрейм профілю
        self.profile_frame = ProfileFrame(
            self.main_container, 
            self.profile_service,
            on_profile_updated=self.on_profile_updated
        )
        
        # Фрейм панелі стану
        self.dashboard_frame = DashboardFrame(
            self.main_container, 
            self.profile_service,
            self.water_log_service
        )
        
        # Фрейм історії
        self.history_frame = HistoryFrame(
            self.main_container, 
            self.water_log_service,
            on_data_changed=self.refresh_dashboard
        )
    
    def check_profile(self):
        """Перевіряє наявність профілю та показує відповідний фрейм."""
        if self.profile_service.has_profile():
            self.show_dashboard_frame()
        else:
            # Показуємо фрейм створення профілю без виведення помилок
            self.show_profile_frame()
            messagebox.showinfo(
                "Вітаємо", 
                "Вітаємо у Water Tracker! Будь ласка, створіть свій профіль для початку роботи."
            )
    
    def show_profile_frame(self):
        """Показує фрейм профілю."""
        self.hide_all_frames()
        self.profile_frame.load_profile()  # Завантажуємо поточний профіль, якщо є
        self.profile_frame.pack(fill=BOTH, expand=YES)
    
    def show_dashboard_frame(self):
        """Показує фрейм панелі стану."""
        if not self.profile_service.has_profile():
            # Показуємо фрейм створення профілю без виведення помилок
            messagebox.showinfo(
                "Створіть профіль", 
                "Спочатку потрібно створити профіль користувача."
            )
            self.show_profile_frame()
            return
        
        self.hide_all_frames()
        self.dashboard_frame.refresh()
        self.dashboard_frame.pack(fill=BOTH, expand=YES)
    
    def show_history_frame(self):
        """Показує фрейм історії."""
        if not self.profile_service.has_profile():
            # Показуємо фрейм створення профілю без виведення помилок
            messagebox.showinfo(
                "Створіть профіль", 
                "Спочатку потрібно створити профіль користувача."
            )
            self.show_profile_frame()
            return
        
        self.hide_all_frames()
        self.history_frame.refresh()
        self.history_frame.pack(fill=BOTH, expand=YES)
    
    def hide_all_frames(self):
        """Приховує всі фрейми."""
        for frame in (self.profile_frame, self.dashboard_frame, self.history_frame):
            frame.pack_forget()
    
    def on_profile_updated(self):
        """Обробник події оновлення профілю."""
        self.show_dashboard_frame()
    
    def refresh_dashboard(self):
        """Оновлює дані на панелі стану."""
        self.dashboard_frame.refresh()
    
    def export_data(self):
        """Експортує дані у файл."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Data"
        )
        
        if not file_path:
            return
        
        if self.data_store.export_data(file_path):
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        else:
            messagebox.showerror("Export Failed", "Failed to export data.")
    
    def import_data(self):
        """Імпортує дані з файлу."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Data"
        )
        
        if not file_path:
            return
        
        if self.data_store.import_data(file_path):
            messagebox.showinfo("Import Successful", "Data imported successfully.")
            # Оновлюємо інтерфейс
            self.check_profile()
        else:
            messagebox.showerror("Import Failed", "Failed to import data.")
    
    def show_about(self):
        """Показує інформацію про програму."""
        messagebox.showinfo(
            "About Water Tracker",
            "Water Tracker v0.1.0\n\n"
            "A simple water tracking application.\n\n"
            "Created with Python and ttkbootstrap."
        ) 