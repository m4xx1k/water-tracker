"""
Frame for managing user profile.
"""

from typing import Callable, Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from model.profile import Gender, Profile
from services.profile_service import ProfileService


class ProfileFrame(ttk.Frame):
    """Frame for creating and editing user profile."""
    
    def __init__(self, parent, profile_service: ProfileService, on_profile_updated: Callable[[], None]):
        """
        Initializes the profile frame.
        
        Args:
            parent: Parent widget.
            profile_service: User profile service.
            on_profile_updated: Callback function called when profile is updated.
        """
        super().__init__(parent)
        
        self.profile_service = profile_service
        self.on_profile_updated = on_profile_updated
        
        # Variables for storing input values
        self.height_var = ttk.IntVar()
        self.weight_var = ttk.DoubleVar()
        self.age_var = ttk.IntVar()
        self.gender_var = ttk.StringVar(value="MALE")
        
        # Set default values
        self.height_var.set(170)
        self.weight_var.set(70.0)
        self.age_var.set(30)
        
        # Create interface
        self.create_widgets()
    
    def create_widgets(self):
        """Creates frame widgets."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=10)
        
        title_label = ttk.Label(
            header_frame, 
            text="Profile Information", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack()
        
        description_label = ttk.Label(
            header_frame,
            text="Enter your information to calculate your daily water intake target.",
            font=("TkDefaultFont", 10)
        )
        description_label.pack(pady=5)
        
        # Profile form
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=BOTH, padx=50, pady=20)
        
        # Height
        height_frame = ttk.Frame(form_frame)
        height_frame.pack(fill=X, pady=10)
        
        height_label = ttk.Label(height_frame, text="Height:", width=10, anchor=W)
        height_label.pack(side=LEFT, padx=(0, 5))
        
        height_entry = ttk.Entry(height_frame, textvariable=self.height_var)
        height_entry.pack(side=LEFT, fill=X, expand=YES)
        
        height_unit = ttk.Label(height_frame, text="cm", width=5)
        height_unit.pack(side=LEFT, padx=5)
        
        # Weight
        weight_frame = ttk.Frame(form_frame)
        weight_frame.pack(fill=X, pady=10)
        
        weight_label = ttk.Label(weight_frame, text="Weight:", width=10, anchor=W)
        weight_label.pack(side=LEFT, padx=(0, 5))
        
        weight_entry = ttk.Entry(weight_frame, textvariable=self.weight_var)
        weight_entry.pack(side=LEFT, fill=X, expand=YES)
        
        weight_unit = ttk.Label(weight_frame, text="kg", width=5)
        weight_unit.pack(side=LEFT, padx=5)
        
        # Age
        age_frame = ttk.Frame(form_frame)
        age_frame.pack(fill=X, pady=10)
        
        age_label = ttk.Label(age_frame, text="Age:", width=10, anchor=W)
        age_label.pack(side=LEFT, padx=(0, 5))
        
        age_entry = ttk.Entry(age_frame, textvariable=self.age_var)
        age_entry.pack(side=LEFT, fill=X, expand=YES)
        
        age_unit = ttk.Label(age_frame, text="years", width=5)
        age_unit.pack(side=LEFT, padx=5)
        
        # Gender
        gender_frame = ttk.Frame(form_frame)
        gender_frame.pack(fill=X, pady=10)
        
        gender_label = ttk.Label(gender_frame, text="Gender:", width=10, anchor=W)
        gender_label.pack(side=LEFT, padx=(0, 5))
        
        for gender in ["MALE", "FEMALE", "OTHER"]:
            gender_radio = ttk.Radiobutton(
                gender_frame, 
                text=gender.capitalize(), 
                variable=self.gender_var, 
                value=gender
            )
            gender_radio.pack(side=LEFT, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, padx=50, pady=20)
        
        save_button = ttk.Button(
            button_frame,
            text="Save Profile",
            command=self.save_profile,
            bootstyle=SUCCESS
        )
        save_button.pack(side=RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_profile_updated,
            bootstyle=SECONDARY
        )
        cancel_button.pack(side=RIGHT, padx=5)
        
        # Calculation information
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, padx=50, pady=20)
        
        info_text = (
            "Daily water intake target is calculated using the formula:\n"
            "((0.035*weight)+(0.002*height)-(0.0002*age)+gender_bonus)*1000\n\n"
            "Gender bonus factors: Male = 0.25, Female = 0.0, Other = 0.15"
        )
        
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("TkDefaultFont", 9),
            justify=LEFT,
            bootstyle=INFO
        )
        info_label.pack(fill=X, pady=5)
    
    def load_profile(self):
        """Loads profile data if it exists."""
        try:
            profile = self.profile_service.get_profile()
            
            if profile:
                # Set field values
                self.height_var.set(profile.height_cm)
                self.weight_var.set(profile.weight_kg)
                self.age_var.set(profile.age_years)
                self.gender_var.set(profile.gender.name)
            # If profile not found, keep default values
        except Exception as e:
            # If error occurred, keep default values
            print(f"Error loading profile: {e}")
    
    def save_profile(self):
        """Saves user profile."""
        try:
            # Get values from fields
            height = self.height_var.get()
            weight = self.weight_var.get()
            age = self.age_var.get()
            gender = self.gender_var.get()
            
            # Validate input data
            if height <= 0 or weight <= 0 or age <= 0:
                ttk.Messagebox.show_error(
                    title="Invalid Input",
                    message="Height, weight, and age must be greater than 0."
                )
                return
            
            # Save profile
            self.profile_service.create_profile(height, weight, age, gender)
            
            # Call callback
            self.on_profile_updated()
            
        except Exception as e:
            ttk.Messagebox.show_error(
                title="Error",
                message=f"Failed to save profile: {str(e)}"
            ) 