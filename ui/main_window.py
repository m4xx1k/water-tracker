"""
Main application window.
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
    """Main application window."""
    
    def __init__(self):
        """Initializes the main application window."""
        super().__init__(title="Water Tracker", themename="cosmo", resizable=(False, False))
        
        # Initialize services
        self.data_store = DataStore()
        self.profile_service = ProfileService(self.data_store)
        self.water_log_service = WaterLogService(self.data_store, self.profile_service)
        
        # Window configuration
        self.geometry("860x600")
        self.position_center()
        
        # Create menu
        self.create_menu()
        
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create frames
        self.create_frames()
        
        # Set initial interface state
        self.check_profile()
    
    def create_menu(self):
        """Creates the main application menu."""
        menu_bar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Data...", command=self.export_data)
        file_menu.add_command(label="Import Data...", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Clear All Data", command=self.clear_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Profile menu
        profile_menu = tk.Menu(menu_bar, tearoff=0)
        profile_menu.add_command(label="Create/Edit Profile", command=self.show_profile_frame)
        menu_bar.add_cascade(label="Profile", menu=profile_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Dashboard", command=self.show_dashboard_frame)
        view_menu.add_command(label="History", command=self.show_history_frame)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
    
    def create_frames(self):
        """Creates the main application frames."""
        # Profile frame
        self.profile_frame = ProfileFrame(
            self.main_container, 
            self.profile_service,
            on_profile_updated=self.on_profile_updated
        )
        
        # Dashboard frame
        self.dashboard_frame = DashboardFrame(
            self.main_container, 
            self.profile_service,
            self.water_log_service
        )
        
        # History frame
        self.history_frame = HistoryFrame(
            self.main_container, 
            self.water_log_service,
            on_data_changed=self.refresh_dashboard
        )
    
    def check_profile(self):
        """Checks for profile existence and shows the appropriate frame."""
        if self.profile_service.has_profile():
            self.show_dashboard_frame()
        else:
            # Show profile creation frame without error messages
            self.show_profile_frame()
            messagebox.showinfo(
                "Welcome", 
                "Welcome to Water Tracker! Please create your profile to get started."
            )
    
    def show_profile_frame(self):
        """Shows the profile frame."""
        self.hide_all_frames()
        self.profile_frame.load_profile()  # Load current profile if exists
        self.profile_frame.pack(fill=BOTH, expand=YES)
    
    def show_dashboard_frame(self):
        """Shows the dashboard frame."""
        if not self.profile_service.has_profile():
            # Show profile creation frame without error messages
            messagebox.showinfo(
                "Create Profile", 
                "You need to create a user profile first."
            )
            self.show_profile_frame()
            return
        
        self.hide_all_frames()
        self.dashboard_frame.refresh()
        self.dashboard_frame.pack(fill=BOTH, expand=YES)
    
    def show_history_frame(self):
        """Shows the history frame."""
        if not self.profile_service.has_profile():
            # Show profile creation frame without error messages
            messagebox.showinfo(
                "Create Profile", 
                "You need to create a user profile first."
            )
            self.show_profile_frame()
            return
        
        self.hide_all_frames()
        self.history_frame.refresh()
        self.history_frame.pack(fill=BOTH, expand=YES)
    
    def hide_all_frames(self):
        """Hides all frames."""
        for frame in (self.profile_frame, self.dashboard_frame, self.history_frame):
            frame.pack_forget()
    
    def on_profile_updated(self):
        """Profile update event handler."""
        self.show_dashboard_frame()
    
    def refresh_dashboard(self):
        """Refreshes dashboard data."""
        self.dashboard_frame.refresh()
    
    def export_data(self):
        """Exports data to a file."""
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
        """Imports data from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Data"
        )
        
        if not file_path:
            return
        
        if self.data_store.import_data(file_path):
            messagebox.showinfo("Import Successful", "Data imported successfully.")
            # Update interface
            self.check_profile()
        else:
            messagebox.showerror("Import Failed", "Failed to import data.")
    
    def show_about(self):
        """Shows information about the application."""
        messagebox.showinfo(
            "About Water Tracker",
            "Water Tracker v0.1.0\n\n"
            "A simple water tracking application.\n\n"
            "Created with Python and ttkbootstrap."
        )
    
    def clear_all_data(self):
        """Clears all application data after confirmation."""
        # Ask for confirmation
        result = messagebox.askquestion(
            "Clear All Data",
            "⚠️ WARNING: This will delete ALL data including your profile and water logs.\n\n"
            "Are you sure you want to continue?",
            icon='warning'
        )
        
        if result != 'yes':
            return
        
        # Clear all data
        try:
            # Clear data store
            self.data_store.clear_all_data()
            
            # Show success message
            messagebox.showinfo(
                "Data Cleared",
                "All data has been successfully cleared.\n"
                "You will now be redirected to create a new profile."
            )
            
            # Redirect to profile creation
            self.show_profile_frame()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to clear data: {str(e)}"
            ) 