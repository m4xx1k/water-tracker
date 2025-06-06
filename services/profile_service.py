"""
Сервіс для роботи з профілем користувача.
"""

from model.profile import Profile, Gender
from repository.data_store import DataStore


class ProfileService:
    """Сервіс для роботи з профілем користувача."""
    
    def __init__(self, data_store: DataStore):
        """
        Ініціалізує сервіс профілю.
        
        Args:
            data_store: Об'єкт сховища даних.
        """
        self.data_store = data_store
    
    def get_profile(self):
        """
        Отримує профіль користувача.
        
        Returns:
            Об'єкт профілю користувача або None, якщо профіль не знайдено.
        """
        return self.data_store.load_profile()
    
    def create_profile(self, height_cm: int, weight_kg: float, 
                     age_years: int, gender: str) -> Profile:
        """
        Створює новий профіль користувача.
        
        Args:
            height_cm: Зріст у сантиметрах.
            weight_kg: Вага у кілограмах.
            age_years: Вік у роках.
            gender: Стать користувача ('MALE', 'FEMALE', 'OTHER').
            
        Returns:
            Створений об'єкт профілю.
            
        Raises:
            ValueError: Якщо вхідні дані некоректні.
        """
        # Валідація вхідних даних
        if height_cm <= 0:
            raise ValueError("Height must be greater than 0 cm.")
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than 0 kg.")
        if age_years <= 0:
            raise ValueError("Age must be greater than 0 years.")
        
        try:
            gender_enum = Gender[gender.upper()]
        except (KeyError, AttributeError):
            raise ValueError(f"Invalid gender. Must be one of: {', '.join([g.name for g in Gender])}.")
        
        # Створення профілю
        profile = Profile(
            height_cm=height_cm,
            weight_kg=weight_kg,
            age_years=age_years,
            gender=gender_enum
        )
        
        # Збереження профілю
        if not self.data_store.save_profile(profile):
            raise RuntimeError("Failed to save profile.")
        
        return profile
    
    def update_profile(self, height_cm: int, weight_kg: float, 
                      age_years: int, gender: str) -> Profile:
        """
        Оновлює профіль користувача.
        
        Args:
            height_cm: Зріст у сантиметрах.
            weight_kg: Вага у кілограмах.
            age_years: Вік у роках.
            gender: Стать користувача ('MALE', 'FEMALE', 'OTHER').
            
        Returns:
            Оновлений об'єкт профілю.
            
        Raises:
            ValueError: Якщо вхідні дані некоректні.
        """
        # Створюємо новий профіль з оновленими даними
        return self.create_profile(height_cm, weight_kg, age_years, gender)
    
    def has_profile(self) -> bool:
        """
        Перевіряє чи створений профіль користувача.
        
        Returns:
            True, якщо профіль створений, інакше False.
        """
        return self.data_store.load_profile() is not None
    
    def get_daily_target(self) -> int:
        """
        Отримує денну норму води.
        
        Returns:
            Денна норма води в мілілітрах або 0, якщо профіль не знайдено.
        """
        profile = self.get_profile()
        if not profile:
            return 0
        return profile.daily_target_ml 