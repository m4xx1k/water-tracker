"""
User profile model.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class Gender(Enum):
    """Enumeration of user gender options."""
    MALE = auto()
    FEMALE = auto()
    OTHER = auto()
    
    def get_bonus(self) -> float:
        """Returns bonus coefficient for daily water norm calculation."""
        if self == Gender.MALE:
            return 0.25
        elif self == Gender.FEMALE:
            return 0.1
        else:  # OTHER
            return 0.15


@dataclass
class Profile:
    """User profile model."""
    height_cm: int
    weight_kg: float
    age_years: int
    gender: Gender
    
    @property
    def daily_target_ml(self) -> int:
        """
        Calculates daily water intake target in milliliters.
        
        Formula: ((0.035*w)+(0.002*h)-(0.0002*a)+gender_bonus)*1000
        where:
        w - weight in kg
        h - height in cm
        a - age in years
        gender_bonus - gender-specific coefficient
        """
        formula = (0.035 * self.weight_kg) + \
                  (0.002 * self.height_cm) - \
                  (0.0002 * self.age_years) + \
                  self.gender.get_bonus()
        
        # Convert to ml and round to nearest integer
        return round(formula * 1000)


@dataclass
class WaterLog:
    """Water consumption record."""
    amount_ml: int
    timestamp: float  # Unix timestamp
    note: Optional[str] = None 