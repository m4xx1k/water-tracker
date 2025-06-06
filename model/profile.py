"""
Модель профілю користувача.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class Gender(Enum):
    """Перелік варіантів статі користувача."""
    MALE = auto()
    FEMALE = auto()
    OTHER = auto()
    
    def get_bonus(self) -> float:
        """Повертає бонусний коефіцієнт для розрахунку денної норми води."""
        if self == Gender.MALE:
            return 0.25
        elif self == Gender.FEMALE:
            return 0.0
        else:  # OTHER
            return 0.15


@dataclass
class Profile:
    """Модель профілю користувача."""
    height_cm: int
    weight_kg: float
    age_years: int
    gender: Gender
    
    @property
    def daily_target_ml(self) -> int:
        """
        Розраховує щоденну норму води в мілілітрах.
        
        Формула: ((0.035*w)+(0.002*h)-(0.0002*a)+gender_bonus)*1000
        де:
        w - вага в кг
        h - зріст в см
        a - вік в роках
        gender_bonus - коефіцієнт залежно від статі
        """
        formula = (0.035 * self.weight_kg) + \
                  (0.002 * self.height_cm) - \
                  (0.0002 * self.age_years) + \
                  self.gender.get_bonus()
        
        # Конвертуємо в мл і округлюємо до найближчого цілого
        return round(formula * 1000)


@dataclass
class WaterLog:
    """Запис про вживання води."""
    amount_ml: int
    timestamp: float  # Unix timestamp
    note: Optional[str] = None 