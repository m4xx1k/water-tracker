"""
Фрейм для перегляду історії вживання води.
"""

import tkinter as tk
from datetime import datetime, timedelta
from typing import Callable, List, Tuple, Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, DatePickerDialog

from model.profile import WaterLog
from services.water_log_service import WaterLogService


class EditWaterLogDialog(tk.Toplevel):
    """Діалог для редагування запису про вживання води."""
    
    def __init__(self, parent, water_log_service: WaterLogService, 
                log_index: int, log: WaterLog, on_edit: Callable[[], None]):
        """
        Ініціалізує діалог редагування запису про вживання води.
        
        Args:
            parent: Батьківський віджет.
            water_log_service: Сервіс записів про вживання води.
            log_index: Індекс запису в списку.
            log: Об'єкт запису про вживання води.
            on_edit: Callback-функція, яка викликається після редагування запису.
        """
        super().__init__(parent)
        self.title("Edit Water Log")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.water_log_service = water_log_service
        self.log_index = log_index
        self.log = log
        self.on_edit = on_edit
        
        # Змінні
        self.amount_var = ttk.IntVar(value=log.amount_ml)
        self.note_var = ttk.StringVar(value=log.note or "")
        
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
        
        # Час запису
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill=X, pady=10)
        
        time_label = ttk.Label(time_frame, text="Time:", width=10, anchor=W)
        time_label.pack(side=LEFT, padx=(0, 5))
        
        time_value = ttk.Label(
            time_frame, 
            text=datetime.fromtimestamp(self.log.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        )
        time_value.pack(side=LEFT, fill=X, expand=YES)
        
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
        
        quick_label = ttk.Label(quick_frame, text="Quick Edit:", width=10, anchor=W)
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
        
        update_button = ttk.Button(
            button_frame, 
            text="Update", 
            command=self.update_water_log,
            bootstyle=SUCCESS
        )
        update_button.pack(side=RIGHT, padx=5)
        
        delete_button = ttk.Button(
            button_frame, 
            text="Delete", 
            command=self.delete_water_log,
            bootstyle=DANGER
        )
        delete_button.pack(side=RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy,
            bootstyle=SECONDARY
        )
        cancel_button.pack(side=RIGHT, padx=5)
    
    def update_water_log(self):
        """Оновлює запис про вживання води."""
        try:
            amount = self.amount_var.get()
            note = self.note_var.get()
            
            if amount <= 0:
                Messagebox.show_error(
                    title="Invalid Input",
                    message="Amount must be greater than 0 ml."
                )
                return
            
            # Оновлюємо запис
            self.water_log_service.update_water_log(self.log_index, amount, note)
            
            # Викликаємо callback
            self.on_edit()
            
            # Закриваємо діалог
            self.destroy()
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to update water log: {str(e)}"
            )
    
    def delete_water_log(self):
        """Видаляє запис про вживання води."""
        try:
            # Видаляємо запис
            self.water_log_service.delete_water_log(self.log_index)
            
            # Викликаємо callback
            self.on_edit()
            
            # Закриваємо діалог
            self.destroy()
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to delete water log: {str(e)}"
            )


class HistoryFrame(ttk.Frame):
    """Фрейм для перегляду історії вживання води."""
    
    def __init__(self, parent, water_log_service: WaterLogService, 
                on_data_changed: Callable[[], None]):
        """
        Ініціалізує фрейм історії.
        
        Args:
            parent: Батьківський віджет.
            water_log_service: Сервіс записів про вживання води.
            on_data_changed: Callback-функція, яка викликається при зміні даних.
        """
        super().__init__(parent)
        
        self.water_log_service = water_log_service
        self.on_data_changed = on_data_changed
        
        # Дати вибірки за замовчуванням (останній тиждень)
        self.end_date = datetime.now().date()
        self.start_date = self.end_date - timedelta(days=7)
        
        # Створення інтерфейсу
        self.create_widgets()
    
    def create_widgets(self):
        """Створює віджети фрейму."""
        # Верхня панель
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=10)
        
        title_label = ttk.Label(
            header_frame, 
            text="Water Consumption History", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack()
        
        # Панель вибору періоду
        date_frame = ttk.Frame(self)
        date_frame.pack(fill=X, padx=20, pady=10)
        
        # Кнопки швидкого вибору періоду
        period_frame = ttk.Frame(date_frame)
        period_frame.pack(side=LEFT, fill=Y)
        
        period_label = ttk.Label(period_frame, text="Period:", anchor=W)
        period_label.pack(side=TOP, anchor=W, pady=(0, 5))
        
        for period, days in [("Today", 1), ("Week", 7), ("Month", 30)]:
            period_button = ttk.Button(
                period_frame,
                text=period,
                command=lambda d=days: self.set_period(d),
                bootstyle=OUTLINE
            )
            period_button.pack(side=LEFT, padx=2)
        
        # Вибір діапазону дат
        range_frame = ttk.Frame(date_frame)
        range_frame.pack(side=RIGHT, fill=Y)
        
        range_label = ttk.Label(range_frame, text="Custom Range:", anchor=W)
        range_label.pack(side=TOP, anchor=W, pady=(0, 5))
        
        date_select_frame = ttk.Frame(range_frame)
        date_select_frame.pack(fill=X)
        
        self.start_date_var = ttk.StringVar(value=self.start_date.strftime("%Y-%m-%d"))
        self.end_date_var = ttk.StringVar(value=self.end_date.strftime("%Y-%m-%d"))
        
        start_date_label = ttk.Label(date_select_frame, text="From:")
        start_date_label.pack(side=LEFT, padx=(0, 5))
        
        # Замінюємо DateEntry на Entry з кнопкою
        start_date_frame = ttk.Frame(date_select_frame)
        start_date_frame.pack(side=LEFT, padx=5)
        
        start_date_entry = ttk.Entry(
            start_date_frame, 
            textvariable=self.start_date_var,
            width=10
        )
        start_date_entry.pack(side=LEFT)
        
        start_date_button = ttk.Button(
            start_date_frame,
            text="📅",
            command=lambda: self.show_date_picker(self.start_date_var),
            width=3
        )
        start_date_button.pack(side=LEFT)
        
        end_date_label = ttk.Label(date_select_frame, text="To:")
        end_date_label.pack(side=LEFT, padx=(10, 5))
        
        # Замінюємо DateEntry на Entry з кнопкою
        end_date_frame = ttk.Frame(date_select_frame)
        end_date_frame.pack(side=LEFT, padx=5)
        
        end_date_entry = ttk.Entry(
            end_date_frame, 
            textvariable=self.end_date_var,
            width=10
        )
        end_date_entry.pack(side=LEFT)
        
        end_date_button = ttk.Button(
            end_date_frame,
            text="📅",
            command=lambda: self.show_date_picker(self.end_date_var),
            width=3
        )
        end_date_button.pack(side=LEFT)
        
        apply_button = ttk.Button(
            date_select_frame,
            text="Apply",
            command=self.apply_date_range,
            bootstyle=INFO
        )
        apply_button.pack(side=LEFT, padx=5)
        
        # Таблиця з історією
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        # Створення таблиці
        columns = ("date", "time", "amount", "note")
        self.history_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        # Заголовки колонок
        self.history_table.heading("date", text="Date")
        self.history_table.heading("time", text="Time")
        self.history_table.heading("amount", text="Amount")
        self.history_table.heading("note", text="Note")
        
        # Ширина колонок
        self.history_table.column("date", width=100)
        self.history_table.column("time", width=100)
        self.history_table.column("amount", width=100)
        self.history_table.column("note", width=400)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.history_table.yview)
        self.history_table.configure(yscroll=scrollbar.set)
        
        # Упаковка таблиці та скролбару
        self.history_table.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Подвійний клік для редагування
        self.history_table.bind("<Double-1>", self.on_item_double_click)
        
        # Статусний рядок
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=X, padx=20, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="",
            anchor=W
        )
        self.status_label.pack(side=LEFT)
        
        # Заповнення таблиці
        self.refresh()
    
    def set_period(self, days: int):
        """
        Встановлює період для відображення історії.
        
        Args:
            days: Кількість днів для відображення.
        """
        self.end_date = datetime.now().date()
        self.start_date = self.end_date - timedelta(days=days - 1)  # -1 для включення поточного дня
        
        # Оновлення змінних
        self.start_date_var.set(self.start_date.strftime("%Y-%m-%d"))
        self.end_date_var.set(self.end_date.strftime("%Y-%m-%d"))
        
        # Оновлення таблиці
        self.refresh()
    
    def apply_date_range(self):
        """Застосовує вибраний діапазон дат."""
        try:
            self.start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
            self.end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
            
            # Перевірка, що початкова дата не пізніше кінцевої
            if self.start_date > self.end_date:
                Messagebox.show_error(
                    title="Invalid Date Range",
                    message="Start date cannot be later than end date."
                )
                return
            
            # Оновлення таблиці
            self.refresh()
            
        except ValueError:
            Messagebox.show_error(
                title="Invalid Date Format",
                message="Please enter dates in the format YYYY-MM-DD."
            )
    
    def refresh(self):
        """Оновлює таблицю історії."""
        try:
            # Очищення таблиці
            for item in self.history_table.get_children():
                self.history_table.delete(item)
            
            # Отримання записів за вказаний період
            start_datetime = datetime.combine(self.start_date, datetime.min.time())
            end_datetime = datetime.combine(self.end_date, datetime.min.time())
            
            logs = self.water_log_service.get_water_logs_by_range(start_datetime, end_datetime)
            
            # Заповнення таблиці
            total_amount = 0
            for index, log in logs:
                log_datetime = datetime.fromtimestamp(log.timestamp)
                date_str = log_datetime.strftime("%Y-%m-%d")
                time_str = log_datetime.strftime("%H:%M")
                amount_str = f"{log.amount_ml} ml"
                note = log.note or ""
                
                self.history_table.insert(
                    "", "end", 
                    values=(date_str, time_str, amount_str, note),
                    tags=(str(index),)  # Зберігаємо індекс запису як тег
                )
                
                total_amount += log.amount_ml
            
            # Оновлення статусного рядка
            logs_count = len(logs)
            period_str = f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}"
            self.status_label.config(
                text=f"Period: {period_str} | Total entries: {logs_count} | Total consumed: {total_amount} ml"
            )
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to refresh history: {str(e)}"
            )
    
    def on_item_double_click(self, event):
        """Обробник подвійного кліку на запис в таблиці."""
        # Отримання вибраного елемента
        selected_item = self.history_table.focus()
        if not selected_item:
            return
        
        # Отримання тегу (індексу запису)
        item_tags = self.history_table.item(selected_item, "tags")
        if not item_tags:
            return
        
        try:
            log_index = int(item_tags[0])
            
            # Отримання запису
            logs = self.water_log_service.get_water_logs()
            for index, log in logs:
                if index == log_index:
                    # Відкриття діалогу редагування
                    dialog = EditWaterLogDialog(
                        self, 
                        self.water_log_service, 
                        log_index, 
                        log, 
                        self.on_log_edited
                    )
                    self.wait_window(dialog)
                    break
        except (ValueError, IndexError) as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to edit log: {str(e)}"
            )
    
    def on_log_edited(self):
        """Обробник події редагування запису."""
        # Оновлення таблиці
        self.refresh()
        
        # Виклик callback
        self.on_data_changed()
    
    def show_date_picker(self, date_var):
        """
        Показує діалог вибору дати.
        
        Args:
            date_var: Змінна для збереження вибраної дати.
        """
        try:
            current_date = datetime.strptime(date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            current_date = datetime.now().date()
            
        dialog = DatePickerDialog(self, firstweekday=0, startdate=current_date)
        selected_date = dialog.date_selected
        
        if selected_date:
            date_var.set(selected_date.strftime("%Y-%m-%d")) 