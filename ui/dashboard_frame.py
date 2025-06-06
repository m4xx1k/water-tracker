"""
Фрейм панелі стану для відображення поточного прогресу вживання води.
"""

import time
import tkinter as tk
from datetime import datetime
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from services.profile_service import ProfileService
from services.water_log_service import WaterLogService


class CircularMeter(ttk.Frame):
    """Віджет для відображення кругового прогрес-бару."""
    
    def __init__(self, parent, **kwargs):
        """
        Ініціалізує круговий індикатор прогресу.
        
        Args:
            parent: Батьківський віджет.
            **kwargs: Додаткові параметри.
        """
        super().__init__(parent, **kwargs)
        
        # Розміри канвасу
        self.size = 200
        self.width = 20  # Товщина лінії
        
        # Канвас для малювання
        self.canvas = tk.Canvas(
            self, 
            width=self.size, 
            height=self.size, 
            background=self.winfo_toplevel().cget("background"),
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Створення дуги
        self.meter_arc = self.canvas.create_arc(
            self.width, self.width, 
            self.size - self.width, self.size - self.width,
            start=90, extent=0, 
            style=tk.ARC, outline="#ddd", width=self.width
        )
        
        # Заповнення
        self.meter_indicator = self.canvas.create_arc(
            self.width, self.width, 
            self.size - self.width, self.size - self.width,
            start=90, extent=0, 
            style=tk.ARC, outline="#007BFF", width=self.width
        )
        
        # Текст з відсотками
        self.percent_text = self.canvas.create_text(
            self.size / 2, self.size / 2,
            text="0%",
            font=("TkDefaultFont", 20, "bold")
        )
        
        # Початкове значення
        self.set_value(0)
    
    def set_value(self, value: float):
        """
        Встановлює значення прогресу.
        
        Args:
            value: Значення від 0 до 1.
        """
        # Обмеження значення від 0 до 1
        value = max(0, min(1, value))
        
        # Оновлення дуги заповнення
        extent = -360 * value
        self.canvas.itemconfig(self.meter_indicator, extent=extent)
        
        # Оновлення тексту
        percent = int(value * 100)
        self.canvas.itemconfig(self.percent_text, text=f"{percent}%")


class WaterLogDialog(tk.Toplevel):
    """Діалог для додавання запису про вживання води."""
    
    def __init__(self, parent, water_log_service: WaterLogService, on_add: callable):
        """
        Ініціалізує діалог додавання запису про вживання води.
        
        Args:
            parent: Батьківський віджет.
            water_log_service: Сервіс записів про вживання води.
            on_add: Callback-функція, яка викликається після додавання запису.
        """
        super().__init__(parent)
        self.title("Add Water Log")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.water_log_service = water_log_service
        self.on_add = on_add
        
        # Змінні
        self.amount_var = ttk.IntVar(value=250)
        self.note_var = ttk.StringVar()
        
        # Віджети
        self.create_widgets()
        
        # Розміщення вікна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Створює віджети діалогу."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # Кількість води
        amount_frame = ttk.Frame(frame)
        amount_frame.pack(fill=X, pady=10)
        
        amount_label = ttk.Label(amount_frame, text="Amount:", width=10, anchor=W)
        amount_label.pack(side=LEFT, padx=(0, 5))
        
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var)
        amount_entry.pack(side=LEFT, fill=X, expand=YES)
        
        amount_unit = ttk.Label(amount_frame, text="ml", width=5)
        amount_unit.pack(side=LEFT, padx=5)
        
        # Кнопки швидкого вибору кількості
        quick_frame = ttk.Frame(frame)
        quick_frame.pack(fill=X, pady=10)
        
        quick_label = ttk.Label(quick_frame, text="Quick Add:", width=10, anchor=W)
        quick_label.pack(side=LEFT, padx=(0, 5))
        
        for amount in [100, 200, 250, 300, 500]:
            quick_button = ttk.Button(
                quick_frame,
                text=f"{amount}ml",
                command=lambda a=amount: self.amount_var.set(a),
                bootstyle=OUTLINE
            )
            quick_button.pack(side=LEFT, padx=2)
        
        # Примітка
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill=X, pady=10)
        
        note_label = ttk.Label(note_frame, text="Note:", width=10, anchor=W)
        note_label.pack(side=LEFT, padx=(0, 5))
        
        note_entry = ttk.Entry(note_frame, textvariable=self.note_var)
        note_entry.pack(side=LEFT, fill=X, expand=YES)
        
        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, pady=(20, 0))
        
        add_button = ttk.Button(
            button_frame, 
            text="Add", 
            command=self.add_water_log,
            bootstyle=SUCCESS
        )
        add_button.pack(side=RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy,
            bootstyle=SECONDARY
        )
        cancel_button.pack(side=RIGHT, padx=5)
    
    def add_water_log(self):
        """Додає запис про вживання води."""
        try:
            amount = self.amount_var.get()
            note = self.note_var.get()
            
            if amount <= 0:
                Messagebox.show_error(
                    title="Invalid Input",
                    message="Amount must be greater than 0 ml."
                )
                return
            
            # Додаємо запис
            self.water_log_service.add_water_log(amount, note)
            
            # Викликаємо callback
            self.on_add()
            
            # Закриваємо діалог
            self.destroy()
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to add water log: {str(e)}"
            )


class DashboardFrame(ttk.Frame):
    """Фрейм панелі стану для відображення поточного прогресу вживання води."""
    
    def __init__(self, parent, profile_service: ProfileService, 
                water_log_service: WaterLogService):
        """
        Ініціалізує фрейм панелі стану.
        
        Args:
            parent: Батьківський віджет.
            profile_service: Сервіс профілю користувача.
            water_log_service: Сервіс записів про вживання води.
        """
        super().__init__(parent)
        
        self.profile_service = profile_service
        self.water_log_service = water_log_service
        
        # Змінні для відображення інформації
        self.target_var = ttk.StringVar()
        self.consumed_var = ttk.StringVar()
        self.last_update_var = ttk.StringVar()
        
        # Створення інтерфейсу
        self.create_widgets()
    
    def create_widgets(self):
        """Створює віджети фрейму."""
        # Верхня панель
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=10)
        
        title_label = ttk.Label(
            header_frame, 
            text="Daily Water Intake", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack()
        
        self.date_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("TkDefaultFont", 10)
        )
        self.date_label.pack(pady=5)
        
        # Контейнер для метрики та інформації
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        # Ліва колонка - круговий індикатор
        meter_frame = ttk.Frame(content_frame)
        meter_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=10)
        
        self.meter = CircularMeter(meter_frame)
        self.meter.pack(pady=20)
        
        # Кнопка додавання запису
        add_button = ttk.Button(
            meter_frame,
            text="Add Water",
            command=self.add_water_log,
            bootstyle=SUCCESS
        )
        add_button.pack(pady=10)
        
        # Права колонка - інформація
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)
        
        # Цільова кількість води
        target_frame = ttk.Frame(info_frame)
        target_frame.pack(fill=X, pady=10)
        
        target_label = ttk.Label(
            target_frame, 
            text="Daily Target:", 
            font=("TkDefaultFont", 10, "bold"),
            width=15,
            anchor=W
        )
        target_label.pack(side=LEFT, padx=5)
        
        target_value = ttk.Label(
            target_frame,
            textvariable=self.target_var,
            font=("TkDefaultFont", 10)
        )
        target_value.pack(side=LEFT, fill=X, expand=YES)
        
        # Спожита кількість води
        consumed_frame = ttk.Frame(info_frame)
        consumed_frame.pack(fill=X, pady=10)
        
        consumed_label = ttk.Label(
            consumed_frame, 
            text="Consumed Today:", 
            font=("TkDefaultFont", 10, "bold"),
            width=15,
            anchor=W
        )
        consumed_label.pack(side=LEFT, padx=5)
        
        consumed_value = ttk.Label(
            consumed_frame,
            textvariable=self.consumed_var,
            font=("TkDefaultFont", 10)
        )
        consumed_value.pack(side=LEFT, fill=X, expand=YES)
        
        # Час останнього оновлення
        update_frame = ttk.Frame(info_frame)
        update_frame.pack(fill=X, pady=10)
        
        update_label = ttk.Label(
            update_frame, 
            text="Last Update:", 
            font=("TkDefaultFont", 10, "bold"),
            width=15,
            anchor=W
        )
        update_label.pack(side=LEFT, padx=5)
        
        update_value = ttk.Label(
            update_frame,
            textvariable=self.last_update_var,
            font=("TkDefaultFont", 10)
        )
        update_value.pack(side=LEFT, fill=X, expand=YES)
        
        # Останні записи
        logs_frame = ttk.LabelFrame(info_frame, text="Recent Logs", padding=10)
        logs_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Список останніх записів
        self.logs_list = ttk.Treeview(
            logs_frame,
            columns=("time", "amount", "note"),
            show="headings",
            height=5
        )
        
        self.logs_list.heading("time", text="Time")
        self.logs_list.heading("amount", text="Amount")
        self.logs_list.heading("note", text="Note")
        
        self.logs_list.column("time", width=100)
        self.logs_list.column("amount", width=100)
        self.logs_list.column("note", width=200)
        
        self.logs_list.pack(fill=BOTH, expand=YES)
        
        # Оновлюємо інформацію
        self.refresh()
    
    def refresh(self):
        """Оновлює інформацію на панелі стану."""
        try:
            # Отримання профілю
            profile = self.profile_service.get_profile()
            if not profile:
                return  # Якщо профіль відсутній, нічого не робимо
                
            # Отримання інформації
            daily_target = self.profile_service.get_daily_target()
            daily_consumption = self.water_log_service.get_daily_consumption()
            progress = self.water_log_service.get_progress_percentage()
            
            # Оновлення відображення
            self.target_var.set(f"{daily_target} ml")
            self.consumed_var.set(f"{daily_consumption} ml")
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            self.meter.set_value(progress)
            
            # Оновлення дати
            self.date_label.config(text=datetime.now().strftime("%A, %B %d, %Y"))
            
            # Оновлення списку останніх записів
            self.update_logs_list()
            
        except Exception as e:
            Messagebox.show_error(
                title="Помилка",
                message=f"Не вдалося оновити панель стану: {str(e)}"
            )
    
    def update_logs_list(self):
        """Оновлює список останніх записів про вживання води."""
        # Очищення списку
        for item in self.logs_list.get_children():
            self.logs_list.delete(item)
        
        # Отримання останніх записів
        logs = self.water_log_service.get_water_logs()
        
        # Заповнення списку
        for index, log in logs:
            time_str = datetime.fromtimestamp(log.timestamp).strftime("%H:%M")
            amount_str = f"{log.amount_ml} ml"
            note = log.note or ""
            
            self.logs_list.insert("", 0, values=(time_str, amount_str, note))
    
    def add_water_log(self):
        """Відкриває діалог для додавання запису про вживання води."""
        dialog = WaterLogDialog(self, self.water_log_service, self.refresh)
        self.wait_window(dialog) 