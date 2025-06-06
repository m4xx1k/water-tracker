"""
Модуль для роботи з даними в JSON файлі.
"""

import json
import os
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from model.profile import Profile, WaterLog, Gender

# Налаштування логування
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='water_tracker.log')
logger = logging.getLogger(__name__)


class DataStore:
    """Клас для зберігання даних у JSON файлі."""
    
    def __init__(self, file_path: str = "watertracker.json"):
        """
        Ініціалізує сховище даних.
        
        Args:
            file_path: Шлях до файлу JSON.
        """
        self.file_path = file_path
        self.data: Dict[str, Any] = {
            "profile": None,
            "water_logs": [],
            "checksum": ""
        }
        
        # Завантажуємо дані з файлу, якщо він існує
        if os.path.exists(file_path):
            self.load()
    
    def _calculate_checksum(self, data_without_checksum: Dict[str, Any]) -> str:
        """
        Розраховує SHA-256 контрольну суму для даних.
        
        Args:
            data_without_checksum: Дані без поля контрольної суми.
            
        Returns:
            Строка з контрольною сумою SHA-256.
        """
        data_str = json.dumps(data_without_checksum, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _verify_checksum(self, data: Dict[str, Any]) -> bool:
        """
        Перевіряє контрольну суму даних.
        
        Args:
            data: Дані з контрольною сумою.
            
        Returns:
            True, якщо контрольна сума співпадає, інакше False.
        """
        expected_checksum = data.get("checksum", "")
        data_copy = data.copy()
        data_copy.pop("checksum", None)
        actual_checksum = self._calculate_checksum(data_copy)
        
        return expected_checksum == actual_checksum
    
    def load(self) -> bool:
        """
        Завантажує дані з JSON файлу.
        
        Returns:
            True, якщо дані успішно завантажені, інакше False.
        """
        try:
            with open(self.file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Перевіряємо контрольну суму
            if not self._verify_checksum(loaded_data):
                logger.warning("Контрольна сума не співпадає.")
                return False
            
            self.data = loaded_data
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Помилка при завантаженні даних: {e}")
            return False
    
    def save(self) -> bool:
        """
        Зберігає дані у JSON файл.
        
        Returns:
            True, якщо дані успішно збережені, інакше False.
        """
        try:
            # Створюємо копію даних без контрольної суми
            data_copy = self.data.copy()
            data_copy.pop("checksum", None)
            
            # Рахуємо нову контрольну суму
            checksum = self._calculate_checksum(data_copy)
            
            # Додаємо контрольну суму та зберігаємо
            self.data["checksum"] = checksum
            
            # Переконуємося, що каталог існує
            os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
            
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Помилка при збереженні даних: {e}")
            return False
    
    def export_data(self, export_path: str) -> bool:
        """
        Експортує дані в JSON файл.
        
        Args:
            export_path: Шлях до файлу експорту.
            
        Returns:
            True, якщо дані успішно експортовані, інакше False.
        """
        try:
            # Копіюємо поточні дані
            export_data = self.data.copy()
            
            # Додаємо метадані експорту
            export_data["export_date"] = time.time()
            
            # Рахуємо нову контрольну суму
            data_without_checksum = export_data.copy()
            data_without_checksum.pop("checksum", None)
            checksum = self._calculate_checksum(data_without_checksum)
            export_data["checksum"] = checksum
            
            # Зберігаємо в файл
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Помилка при експорті даних: {e}")
            return False
    
    def import_data(self, import_path: str) -> bool:
        """
        Імпортує дані з JSON файлу.
        
        Args:
            import_path: Шлях до файлу імпорту.
            
        Returns:
            True, якщо дані успішно імпортовані, інакше False.
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            # Перевіряємо контрольну суму
            if not self._verify_checksum(import_data):
                logger.warning("Контрольна сума імпортованих даних не співпадає.")
                return False
            
            # Оновлюємо дані
            self.data = import_data
            
            # Зберігаємо оновлені дані
            return self.save()
        except Exception as e:
            logger.error(f"Помилка при імпорті даних: {e}")
            return False
    
    def save_profile(self, profile: Profile) -> bool:
        """
        Зберігає профіль користувача.
        
        Args:
            profile: Об'єкт профілю користувача.
            
        Returns:
            True, якщо профіль успішно збережений, інакше False.
        """
        try:
            # Конвертуємо профіль в словник
            profile_dict = {
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "age_years": profile.age_years,
                "gender": profile.gender.name
            }
            
            self.data["profile"] = profile_dict
            return self.save()
        except Exception as e:
            logger.error(f"Помилка при збереженні профілю: {e}")
            return False
    
    def load_profile(self) -> Optional[Profile]:
        """
        Завантажує профіль користувача.
        
        Returns:
            Об'єкт профілю або None, якщо профіль не знайдено.
        """
        profile_dict = self.data.get("profile")
        if not profile_dict:
            return None
            
        try:
            return Profile(
                height_cm=profile_dict["height_cm"],
                weight_kg=profile_dict["weight_kg"],
                age_years=profile_dict["age_years"],
                gender=Gender[profile_dict["gender"]]
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Помилка при завантаженні профілю: {e}")
            return None
    
    def add_water_log(self, water_log: WaterLog) -> bool:
        """
        Додає запис про вживання води.
        
        Args:
            water_log: Об'єкт запису про вживання води.
            
        Returns:
            True, якщо запис успішно доданий, інакше False.
        """
        try:
            # Конвертуємо запис в словник
            log_dict = {
                "amount_ml": water_log.amount_ml,
                "timestamp": water_log.timestamp,
                "note": water_log.note
            }
            
            self.data["water_logs"].append(log_dict)
            return self.save()
        except Exception as e:
            logger.error(f"Помилка при додаванні запису про вживання води: {e}")
            return False
    
    def update_water_log(self, index: int, water_log: WaterLog) -> bool:
        """
        Оновлює запис про вживання води.
        
        Args:
            index: Індекс запису.
            water_log: Оновлений об'єкт запису.
            
        Returns:
            True, якщо запис успішно оновлений, інакше False.
        """
        try:
            if 0 <= index < len(self.data["water_logs"]):
                # Конвертуємо запис в словник
                log_dict = {
                    "amount_ml": water_log.amount_ml,
                    "timestamp": water_log.timestamp,
                    "note": water_log.note
                }
                
                self.data["water_logs"][index] = log_dict
                return self.save()
            else:
                logger.warning(f"Помилка: Індекс {index} за межами діапазону записів.")
                return False
        except Exception as e:
            logger.error(f"Помилка при оновленні запису про вживання води: {e}")
            return False
    
    def delete_water_log(self, index: int) -> bool:
        """
        Видаляє запис про вживання води.
        
        Args:
            index: Індекс запису.
            
        Returns:
            True, якщо запис успішно видалений, інакше False.
        """
        try:
            if 0 <= index < len(self.data["water_logs"]):
                del self.data["water_logs"][index]
                return self.save()
            else:
                logger.warning(f"Помилка: Індекс {index} за межами діапазону записів.")
                return False
        except Exception as e:
            logger.error(f"Помилка при видаленні запису про вживання води: {e}")
            return False
    
    def get_water_logs(self, start_time: Optional[float] = None, 
                      end_time: Optional[float] = None) -> List[Tuple[int, WaterLog]]:
        """
        Отримує список записів про вживання води за вказаний період.
        
        Args:
            start_time: Початок періоду (Unix timestamp).
            end_time: Кінець періоду (Unix timestamp).
            
        Returns:
            Список кортежів (індекс, запис) про вживання води.
        """
        logs = []
        
        for i, log_dict in enumerate(self.data.get("water_logs", [])):
            timestamp = log_dict.get("timestamp", 0)
            
            # Перевіряємо, чи входить запис у вказаний період
            if ((start_time is None or timestamp >= start_time) and 
                (end_time is None or timestamp <= end_time)):
                
                log = WaterLog(
                    amount_ml=log_dict.get("amount_ml", 0),
                    timestamp=timestamp,
                    note=log_dict.get("note")
                )
                
                logs.append((i, log))
        
        return logs 