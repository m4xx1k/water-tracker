"""
Сервіс для роботи з записами про вживання води.
"""

import time
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

from model.profile import WaterLog
from repository.data_store import DataStore
from services.profile_service import ProfileService


class WaterLogService:
    """Сервіс для роботи з записами про вживання води."""
    
    def __init__(self, data_store: DataStore, profile_service: ProfileService):
        """
        Ініціалізує сервіс записів про вживання води.
        
        Args:
            data_store: Об'єкт сховища даних.
            profile_service: Сервіс профілю користувача.
        """
        self.data_store = data_store
        self.profile_service = profile_service
    
    def add_water_log(self, amount_ml: int, note: Optional[str] = None) -> WaterLog:
        """
        Додає новий запис про вживання води.
        
        Args:
            amount_ml: Кількість випитої води в мілілітрах.
            note: Примітка до запису.
            
        Returns:
            Створений об'єкт запису.
            
        Raises:
            ValueError: Якщо вхідні дані некоректні.
        """
        # Валідація вхідних даних
        if amount_ml <= 0:
            raise ValueError("Amount must be greater than 0 ml.")
        
        # Створення запису
        water_log = WaterLog(
            amount_ml=amount_ml,
            timestamp=time.time(),
            note=note
        )
        
        # Збереження запису
        if not self.data_store.add_water_log(water_log):
            raise RuntimeError("Failed to save water log.")
        
        return water_log
    
    def update_water_log(self, index: int, amount_ml: int, 
                        note: Optional[str] = None) -> WaterLog:
        """
        Оновлює запис про вживання води.
        
        Args:
            index: Індекс запису.
            amount_ml: Нова кількість випитої води в мілілітрах.
            note: Нова примітка до запису.
            
        Returns:
            Оновлений об'єкт запису.
            
        Raises:
            ValueError: Якщо вхідні дані некоректні.
            IndexError: Якщо індекс за межами діапазону.
        """
        # Валідація вхідних даних
        if amount_ml <= 0:
            raise ValueError("Amount must be greater than 0 ml.")
        
        # Отримання поточного запису
        logs = self.data_store.get_water_logs()
        if index < 0 or index >= len(logs):
            raise IndexError(f"Log index {index} out of range.")
        
        _, current_log = logs[index]
        
        # Створення оновленого запису
        updated_log = WaterLog(
            amount_ml=amount_ml,
            timestamp=current_log.timestamp,
            note=note
        )
        
        # Збереження оновленого запису
        if not self.data_store.update_water_log(index, updated_log):
            raise RuntimeError("Failed to update water log.")
        
        return updated_log
    
    def delete_water_log(self, index: int) -> None:
        """
        Видаляє запис про вживання води.
        
        Args:
            index: Індекс запису.
            
        Raises:
            IndexError: Якщо індекс за межами діапазону.
        """
        # Перевірка існування запису
        logs = self.data_store.get_water_logs()
        if index < 0 or index >= len(logs):
            raise IndexError(f"Log index {index} out of range.")
        
        # Видалення запису
        if not self.data_store.delete_water_log(index):
            raise RuntimeError("Failed to delete water log.")
    
    def get_water_logs(self, days: int = 1) -> List[Tuple[int, WaterLog]]:
        """
        Отримує список записів про вживання води за вказаний період.
        
        Args:
            days: Кількість днів для виборки (за замовчуванням - 1 день).
            
        Returns:
            Список кортежів (індекс, запис) про вживання води.
        """
        # Розрахунок часового періоду
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)  # days to seconds
        
        # Отримання записів
        return self.data_store.get_water_logs(start_time, end_time)
    
    def get_water_logs_by_range(self, start_date: datetime, 
                               end_date: datetime) -> List[Tuple[int, WaterLog]]:
        """
        Отримує список записів про вживання води за вказаний діапазон дат.
        
        Args:
            start_date: Початкова дата.
            end_date: Кінцева дата.
            
        Returns:
            Список кортежів (індекс, запис) про вживання води.
        """
        # Перетворення дат в Unix timestamp
        # Додаємо 1 день до кінцевої дати, щоб включити її в період
        end_date = end_date + timedelta(days=1)
        
        start_time = start_date.timestamp()
        end_time = end_date.timestamp()
        
        # Отримання записів
        return self.data_store.get_water_logs(start_time, end_time)
    
    def get_daily_consumption(self) -> int:
        """
        Отримує загальне споживання води за поточний день.
        
        Returns:
            Кількість випитої води в мілілітрах.
        """
        # Отримуємо записи за поточний день
        logs = self.get_water_logs(days=1)
        
        # Підсумовуємо кількість води
        return sum(log.amount_ml for _, log in logs)
    
    def get_progress_percentage(self) -> float:
        """
        Розраховує відсоток виконання денної норми води.
        
        Returns:
            Відсоток виконання (від 0.0 до 1.0).
        """
        # Отримуємо денну норму води
        daily_target = self.profile_service.get_daily_target()
        
        # Якщо профіль відсутній або норма води = 0
        if daily_target == 0:
            return 0.0
        
        # Отримуємо поточне споживання
        current_consumption = self.get_daily_consumption()
        
        # Розраховуємо відсоток
        return min(1.0, current_consumption / daily_target) 