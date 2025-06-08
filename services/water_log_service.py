"""
Service for managing water consumption records.
"""

import time
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

from model.profile import WaterLog
from repository.data_store import DataStore
from services.profile_service import ProfileService


class WaterLogService:
    """Service for managing water consumption records."""
    
    def __init__(self, data_store: DataStore, profile_service: ProfileService):
        """
        Initializes the water log service.
        
        Args:
            data_store: Data storage object.
            profile_service: User profile service.
        """
        self.data_store = data_store
        self.profile_service = profile_service
    
    def add_water_log(self, amount_ml: int, note: Optional[str] = None) -> WaterLog:
        """
        Adds a new water consumption record.
        
        Args:
            amount_ml: Amount of water consumed in milliliters.
            note: Note for the record.
            
        Returns:
            Created water log object.
            
        Raises:
            ValueError: If input data is invalid.
        """
        # Validate input data
        if amount_ml <= 0:
            raise ValueError("Amount must be greater than 0 ml.")
        
        # Create record
        water_log = WaterLog(
            amount_ml=amount_ml,
            timestamp=time.time(),
            note=note
        )
        
        # Save record
        if not self.data_store.add_water_log(water_log):
            raise RuntimeError("Failed to save water log.")
        
        return water_log
    
    def update_water_log(self, index: int, amount_ml: int, 
                        note: Optional[str] = None) -> WaterLog:
        """
        Updates a water consumption record.
        
        Args:
            index: Record index.
            amount_ml: New amount of water consumed in milliliters.
            note: New note for the record.
            
        Returns:
            Updated water log object.
            
        Raises:
            ValueError: If input data is invalid.
            IndexError: If index is out of range.
        """
        # Validate input data
        if amount_ml <= 0:
            raise ValueError("Amount must be greater than 0 ml.")
        
        # Retrieve current record
        logs = self.data_store.get_water_logs()
        if index < 0 or index >= len(logs):
            raise IndexError(f"Log index {index} out of range.")
        
        _, current_log = logs[index]
        
        # Create updated record
        updated_log = WaterLog(
            amount_ml=amount_ml,
            timestamp=current_log.timestamp,
            note=note
        )
        
        # Save updated record
        if not self.data_store.update_water_log(index, updated_log):
            raise RuntimeError("Failed to update water log.")
        
        return updated_log
    
    def delete_water_log(self, index: int) -> None:
        """
        Deletes a water consumption record.
        
        Args:
            index: Record index.
            
        Raises:
            IndexError: If index is out of range.
        """
        # Check if record exists
        logs = self.data_store.get_water_logs()
        if index < 0 or index >= len(logs):
            raise IndexError(f"Log index {index} out of range.")
        
        # Delete record
        if not self.data_store.delete_water_log(index):
            raise RuntimeError("Failed to delete water log.")
    
    def get_water_logs(self, days: int = 1) -> List[Tuple[int, WaterLog]]:
        """
        Retrieves a list of water consumption records for the specified period.
        
        Args:
            days: Number of days to retrieve (default is 1 day).
            
        Returns:
            List of tuples (index, water log) of water consumption records.
        """
        # Calculate time period
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)  # days to seconds
        
        # Retrieve records
        return self.data_store.get_water_logs(start_time, end_time)
    
    def get_water_logs_by_range(self, start_date: datetime, 
                               end_date: datetime) -> List[Tuple[int, WaterLog]]:
        """
        Retrieves a list of water consumption records for the specified date range.
        
        Args:
            start_date: Start date.
            end_date: End date.
            
        Returns:
            List of tuples (index, water log) of water consumption records.
        """
        # Convert dates to Unix timestamp
        # Add 1 day to the end date to include it in the range
        end_date = end_date + timedelta(days=1)
        
        start_time = start_date.timestamp()
        end_time = end_date.timestamp()
        
        # Retrieve records
        return self.data_store.get_water_logs(start_time, end_time)
    
    def get_daily_consumption(self) -> int:
        """
        Retrieves total water consumption for the current day.
        
        Returns:
            Amount of water consumed in milliliters.
        """
        # Retrieve records for the current day
        logs = self.get_water_logs(days=1)
        
        # Sum the amount of water
        return sum(log.amount_ml for _, log in logs)
    
    def get_progress_percentage(self) -> float:
        """
        Calculates the percentage of daily water target achieved.
        
        Returns:
            Percentage of target achieved (from 0.0 to 1.0).
        """
        # Retrieve daily water target
        daily_target = self.profile_service.get_daily_target()
        
        # If profile is missing or target is 0
        if daily_target == 0:
            return 0.0
        
        # Retrieve current consumption
        current_consumption = self.get_daily_consumption()
        
        # Calculate percentage
        return min(1.0, current_consumption / daily_target) 