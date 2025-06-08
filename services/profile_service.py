"""
Service for working with user profile.
"""

from model.profile import Profile, Gender
from repository.data_store import DataStore


class ProfileService:
    """Service for working with user profile."""
    
    def __init__(self, data_store: DataStore):
        """
        Initializes the profile service.
        
        Args:
            data_store: Data storage object.
        """
        self.data_store = data_store
    
    def get_profile(self):
        """
        Retrieves the user profile.
        
        Returns:
            User profile object or None if not found.
        """
        return self.data_store.load_profile()
    
    def create_profile(self, height_cm: int, weight_kg: float,
                     age_years: int, gender: str) -> Profile:
        """
        Creates a new user profile.
        
        Args:
            height_cm: Height in centimeters.
            weight_kg: Weight in kilograms.
            age_years: Age in years.
            gender: User gender ('MALE', 'FEMALE', 'OTHER').
            
        Returns:
            Created profile object.
            
        Raises:
            ValueError: If input data is invalid.
        """
        # Input data validation
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
        
        # Create profile
        profile = Profile(
            height_cm=height_cm,
            weight_kg=weight_kg,
            age_years=age_years,
            gender=gender_enum
        )
        
        # Save profile
        if not self.data_store.save_profile(profile):
            raise RuntimeError("Failed to save profile.")
        
        return profile
    
    def update_profile(self, height_cm: int, weight_kg: float,
                      age_years: int, gender: str) -> Profile:
        """
        Updates user profile.
        
        Args:
            height_cm: Height in centimeters.
            weight_kg: Weight in kilograms.
            age_years: Age in years.
            gender: User gender ('MALE', 'FEMALE', 'OTHER').
            
        Returns:
            Updated profile object.
            
        Raises:
            ValueError: If input data is invalid.
        """
        # Create new profile with updated data
        return self.create_profile(height_cm, weight_kg, age_years, gender)
    
    def has_profile(self) -> bool:
        """
        Checks if user profile exists.
        
        Returns:
            True if profile exists, otherwise False.
        """
        return self.data_store.load_profile() is not None
    
    def get_daily_target(self) -> int:
        """
        Gets daily water target.
        
        Returns:
            Daily water target in milliliters or 0 if profile not found.
        """
        profile = self.get_profile()
        if not profile:
            return 0
        return profile.daily_target_ml 