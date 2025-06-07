"""
Dashboard frame for displaying current water consumption progress.
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


class ModernCircularMeter(ttk.Frame):
    """Modern widget for displaying circular progress bar with background."""
    
    def __init__(self, parent, **kwargs):
        """
        Initializes modern circular progress indicator.
        
        Args:
            parent: Parent widget.
            **kwargs: Additional parameters.
        """
        super().__init__(parent, **kwargs)
        
        # Canvas dimensions
        self.size = 200
        self.width = 20  # Line thickness
        self.center = self.size // 2
        
        # Colors
        self.bg_color = "#e9ecef"
        self.progress_color = "#0d6efd"
        self.text_color = "#212529"
        self.accent_color = "#198754"
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            self, 
            width=self.size, 
            height=self.size, 
            background=self.winfo_toplevel().cget("background"),
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Background circle
        self.bg_arc = self.canvas.create_arc(
            self.width//2, self.width//2, 
            self.size - self.width//2, self.size - self.width//2,
            start=0, extent=360, 
            style=tk.ARC, outline=self.bg_color, width=self.width
        )
        
        # Progress arc
        self.progress_arc = self.canvas.create_arc(
            self.width//2, self.width//2, 
            self.size - self.width//2, self.size - self.width//2,
            start=90, extent=0, 
            style=tk.ARC, outline=self.progress_color, width=self.width
        )
        
        # Center circle background
        center_radius = 50
        self.center_bg = self.canvas.create_oval(
            self.center - center_radius, self.center - center_radius,
            self.center + center_radius, self.center + center_radius,
            fill="white", outline=self.bg_color, width=2
        )
        
        # Percentage text
        self.percent_text = self.canvas.create_text(
            self.center, self.center - 8,
            text="0%",
            font=("TkDefaultFont", 20, "bold"),
            fill=self.text_color
        )
        
        # Status text
        self.status_text = self.canvas.create_text(
            self.center, self.center + 12,
            text="Start!",
            font=("TkDefaultFont", 9),
            fill="#6c757d"
        )
        
        # Initial value
        self.current_value = 0
        self.target_value = 0
        self.set_value(0)
    
    def set_value(self, value: float, consumed: int = 0, target: int = 0):
        """
        Sets progress value with animation effect.
        
        Args:
            value: Progress value from 0 to 1.
            consumed: Amount consumed in ml.
            target: Target amount in ml.
        """
        self.target_value = max(0, min(1, value))
        self.consumed = consumed
        self.target = target
        
        # Simple update without complex animation
        self.current_value = self.target_value
        self._update_display()
    
    def _update_display(self):
        """Updates the visual display."""
        # Update progress arc
        extent = -360 * self.current_value
        self.canvas.itemconfig(self.progress_arc, extent=extent)
        
        # Update color based on progress
        if self.current_value >= 1.0:
            color = self.accent_color
            status = "Done! 🎉"
        elif self.current_value >= 0.7:
            color = "#fd7e14"  # Orange
            status = "Almost!"
        elif self.current_value >= 0.3:
            color = self.progress_color
            status = "Going!"
        else:
            color = self.progress_color
            status = "Start!"
        
        self.canvas.itemconfig(self.progress_arc, outline=color)
        
        # Update text
        percent = int(self.current_value * 100)
        self.canvas.itemconfig(self.percent_text, text=f"{percent}%")
        self.canvas.itemconfig(self.status_text, text=status)


class WaterLogDialog(tk.Toplevel):
    """Simple dialog for adding water log entries."""
    
    def __init__(self, parent, water_log_service: WaterLogService, on_add: callable):
        """Initialize water log dialog."""
        super().__init__(parent)
        self.title("Add Water")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.water_log_service = water_log_service
        self.on_add = on_add
        
        # Variables
        self.amount_var = ttk.IntVar(value=250)
        self.note_var = ttk.StringVar()
        
        # Create widgets
        self.create_widgets()
        
        # Center and size window properly
        self.update_idletasks()
        width = 450  # Increased width
        height = 350  # Increased height
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="💧 Add Water",
            font=("TkDefaultFont", 14, "bold"),
            foreground="#0d6efd"
        )
        title_label.pack(pady=(0, 15))
        
        # Amount section
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(amount_frame, text="Amount:", font=("TkDefaultFont", 10)).pack(anchor=W, pady=(0, 5))
        
        # Amount entry row
        entry_row = ttk.Frame(amount_frame)
        entry_row.pack(fill=X)
        
        amount_entry = ttk.Entry(
            entry_row, 
            textvariable=self.amount_var,
            font=("TkDefaultFont", 12),
            width=8
        )
        amount_entry.pack(side=LEFT, padx=(0, 8))
        
        ttk.Label(entry_row, text="ml", font=("TkDefaultFont", 12)).pack(side=LEFT)
        
        # Quick buttons (simplified)
        quick_frame = ttk.Frame(amount_frame)
        quick_frame.pack(fill=X, pady=(10, 0))
        
        amounts = [100, 200, 250, 300, 500]
        for amount in amounts:
            btn = ttk.Button(
                quick_frame,
                text=f"{amount}",
                command=lambda a=amount: self.amount_var.set(a),
                bootstyle="outline",
                width=6
            )
            btn.pack(side=LEFT, padx=(0, 5))
        
        # Note section
        note_frame = ttk.Frame(main_frame)
        note_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(note_frame, text="Note (optional):", font=("TkDefaultFont", 10)).pack(anchor=W, pady=(0, 5))
        
        note_entry = ttk.Entry(
            note_frame, 
            textvariable=self.note_var,
            font=("TkDefaultFont", 11)
        )
        note_entry.pack(fill=X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy,
            width=10
        ).pack(side=LEFT)
        
        ttk.Button(
            button_frame, 
            text="Add", 
            command=self.add_water_log,
            bootstyle="success",
            width=10
        ).pack(side=RIGHT)
        
        # Focus
        amount_entry.focus()
        amount_entry.select_range(0, tk.END)
    
    def add_water_log(self):
        """Add water log entry."""
        try:
            amount = self.amount_var.get()
            note = self.note_var.get().strip()
            
            if amount <= 0:
                Messagebox.show_error(
                    title="Invalid Input",
                    message="Amount must be greater than 0 ml."
                )
                return
            
            if amount > 2000:
                Messagebox.show_error(
                    title="Too Much Water!",
                    message="Single intake cannot exceed 2000ml for health safety."
                )
                return
            
            # Check daily limit
            daily_consumption = self.water_log_service.get_daily_consumption()
            if daily_consumption + amount > 8000:  # 8L daily limit
                Messagebox.show_warning(
                    title="Daily Limit Warning",
                    message=f"Adding {amount}ml would exceed safe daily limit (8L).\nCurrent: {daily_consumption}ml"
                )
                return
            
            self.water_log_service.add_water_log(amount, note if note else None)
            self.on_add()
            self.destroy()
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to add water log: {str(e)}"
            )


class DashboardFrame(ttk.Frame):
    """Simple dashboard frame for water consumption tracking."""
    
    def __init__(self, parent, profile_service: ProfileService, 
                water_log_service: WaterLogService):
        """Initialize dashboard frame."""
        super().__init__(parent)
        
        self.profile_service = profile_service
        self.water_log_service = water_log_service
        
        # Display variables
        self.target_var = ttk.StringVar()
        self.consumed_var = ttk.StringVar()
        self.remaining_var = ttk.StringVar()
        
        # Create interface
        self.create_widgets()
    
    def create_widgets(self):
        """Create dashboard widgets."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(15, 20))
        
        title_label = ttk.Label(
            header_frame, 
            text="💧 Daily Water Intake", 
            font=("TkDefaultFont", 16, "bold"),
            foreground="#0d6efd"
        )
        title_label.pack()
        
        self.date_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("TkDefaultFont", 10),
            foreground="#6c757d"
        )
        self.date_label.pack(pady=(2, 0))
        
        # Motivational subtitle
        self.motivation_label = ttk.Label(
            header_frame,
            text="Stay hydrated, stay healthy! 🌟",
            font=("TkDefaultFont", 9),
            foreground="#198754"
        )
        self.motivation_label.pack(pady=(2, 0))
        
        # Main content
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=BOTH, expand=YES, padx=20)
        
        # Left side - Progress
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 15))
        
        # Progress meter
        progress_frame = ttk.LabelFrame(left_frame, text="Progress", padding=15)
        progress_frame.pack(fill=X, pady=(0, 15))
        
        self.meter = ModernCircularMeter(progress_frame)
        self.meter.pack()
        
        # Quick add buttons
        quick_frame = ttk.LabelFrame(left_frame, text="🚿 Quick Add Water", padding=15)
        quick_frame.pack(fill=X)
        
        buttons_row = ttk.Frame(quick_frame)
        buttons_row.pack()
        
        amounts = [("💧 100ml", 100), ("☕ 200ml", 200), ("🥤 250ml", 250), ("🍶 350ml", 350), ("🚰 500ml", 500)]
        for text, amount in amounts:
            btn = ttk.Button(
                buttons_row,
                text=text,
                command=lambda a=amount: self.quick_add_water(a),
                bootstyle="primary-outline",
                width=9
            )
            btn.pack(side=LEFT, padx=1)
        
        # Custom button
        ttk.Button(
            quick_frame,
            text="➕ Custom",
            command=self.add_water_log,
            bootstyle="success",
            width=15
        ).pack(pady=(10, 0))
        
        # Right side - Stats and logs
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(15, 0))
        
        # Stats
        stats_frame = ttk.LabelFrame(right_frame, text="📊 Today's Progress", padding=15)
        stats_frame.pack(fill=X, pady=(0, 15))
        
        # Create simple stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=X)
        
        # Row 1 - Target
        row1 = ttk.Frame(stats_grid)
        row1.pack(fill=X, pady=3)
        ttk.Label(row1, text="🎯 Target:", width=12, foreground="#6c757d").pack(side=LEFT)
        ttk.Label(row1, textvariable=self.target_var, font=("TkDefaultFont", 10, "bold"), foreground="#0d6efd").pack(side=LEFT)
        
        # Row 2 - Consumed
        row2 = ttk.Frame(stats_grid)
        row2.pack(fill=X, pady=3)
        ttk.Label(row2, text="💙 Consumed:", width=12, foreground="#6c757d").pack(side=LEFT)
        self.consumed_label = ttk.Label(row2, textvariable=self.consumed_var, font=("TkDefaultFont", 10, "bold"), foreground="#198754")
        self.consumed_label.pack(side=LEFT)
        
        # Row 3 - Remaining
        row3 = ttk.Frame(stats_grid)
        row3.pack(fill=X, pady=3)
        ttk.Label(row3, text="⏰ Remaining:", width=12, foreground="#6c757d").pack(side=LEFT)
        self.remaining_label = ttk.Label(row3, textvariable=self.remaining_var, font=("TkDefaultFont", 10, "bold"), foreground="#fd7e14")
        self.remaining_label.pack(side=LEFT)
        
        # Logs section
        logs_frame = ttk.LabelFrame(right_frame, text="💦 Recent Activity", padding=10)
        logs_frame.pack(fill=BOTH, expand=YES)
        
        # Simple logs display using Treeview
        self.logs_tree = ttk.Treeview(
            logs_frame,
            columns=("time", "amount"),  
            show="headings",
            height=8
        )
        
        # Configure columns
        self.logs_tree.heading("time", text="🕐 Time")
        self.logs_tree.heading("amount", text="💧 Amount")
        
        self.logs_tree.column("time", width=100, anchor="center")
        self.logs_tree.column("amount", width=120, anchor="center")
        
        # Style the treeview
        self.logs_tree.pack(fill=BOTH, expand=YES)
        
        # Refresh data
        self.refresh()
    
    def quick_add_water(self, amount: int):
        """Quick add water with specified amount."""
        try:
            # Check daily limit
            daily_consumption = self.water_log_service.get_daily_consumption()
            if daily_consumption + amount > 8000:  # 8L daily limit
                Messagebox.show_warning(
                    title="Daily Limit Warning",
                    message=f"Adding {amount}ml would exceed safe daily limit (8L).\nCurrent: {daily_consumption}ml"
                )
                return
            
            self.water_log_service.add_water_log(amount, f"Quick add")
            self.refresh()
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to add water log: {str(e)}"
            )
    
    def refresh(self):
        """Refresh dashboard information."""
        try:
            # Get profile
            profile = self.profile_service.get_profile()
            if not profile:
                return
                
            # Get information
            daily_target = self.profile_service.get_daily_target()
            daily_consumption = self.water_log_service.get_daily_consumption()
            progress = self.water_log_service.get_progress_percentage()
            remaining = max(0, daily_target - daily_consumption)
            
            # Update display
            self.target_var.set(f"{daily_target} ml")
            self.consumed_var.set(f"{daily_consumption} ml")
            self.remaining_var.set(f"{remaining} ml")
            
            # Update colors based on progress
            if progress >= 1.0:
                self.consumed_label.config(foreground="#198754")  # Green - goal reached
                self.remaining_label.config(foreground="#6c757d")  # Gray - done
            elif progress >= 0.7:
                self.consumed_label.config(foreground="#fd7e14")  # Orange - close
                self.remaining_label.config(foreground="#dc3545")  # Red - urgent
            else:
                self.consumed_label.config(foreground="#0d6efd")  # Blue - normal
                self.remaining_label.config(foreground="#fd7e14")  # Orange - needs attention
            
            # Update meter
            self.meter.set_value(progress, daily_consumption, daily_target)
            
            # Update date
            self.date_label.config(text=datetime.now().strftime("%A, %B %d, %Y"))
            
            # Update motivational message based on progress
            if progress >= 1.0:
                motivation = "Excellent! Goal achieved! 🏆"
            elif progress >= 0.8:
                motivation = "Almost there! Keep going! 🚀"
            elif progress >= 0.5:
                motivation = "Great progress! You're doing well! 💪"
            elif progress >= 0.2:
                motivation = "Good start! Keep drinking! 🌊"
            else:
                motivation = "Stay hydrated, stay healthy! 🌟"
            
            self.motivation_label.config(text=motivation)
            
            # Update logs
            self.update_logs_list()
            
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to refresh dashboard: {str(e)}"
            )
    
    def update_logs_list(self):
        """Update logs list."""
        # Clear existing logs
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Get recent logs
        logs = self.water_log_service.get_water_logs()
        
        if not logs:
            # Show empty state
            self.logs_tree.insert("", "end", values=("--:--", "🏜️ Поки пусто"))
            self.logs_tree.insert("", "end", values=("Додай!", "💧 Першу воду"))
        else:
            # Sort logs by timestamp (newest first) and show last 10
            sorted_logs = sorted(logs, key=lambda x: x[1].timestamp, reverse=True)[:10]
            
            for index, log in sorted_logs:
                time_str = datetime.fromtimestamp(log.timestamp).strftime("%H:%M")
                
                # Amount with colorful emojis
                if log.amount_ml >= 500:
                    amount_str = f"🚰 {log.amount_ml}ml"  # Large
                elif log.amount_ml >= 300:
                    amount_str = f"🥤 {log.amount_ml}ml"  # Medium
                elif log.amount_ml >= 200:
                    amount_str = f"🧊 {log.amount_ml}ml"  # Small-medium
                else:
                    amount_str = f"💧 {log.amount_ml}ml"  # Small
                
                # Add to tree (already sorted newest first)
                self.logs_tree.insert("", "end", values=(time_str, amount_str))
    
    def add_water_log(self):
        """Open dialog for adding water log entry."""
        dialog = WaterLogDialog(self, self.water_log_service, self.refresh)
        self.wait_window(dialog) 