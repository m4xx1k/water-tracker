"""
Module for working with JSON data files.
"""

import json
import os
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from model.profile import Profile, WaterLog, Gender

# Logging configuration
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='water_tracker.log')
logger = logging.getLogger(__name__)


class DataStore:
    """Class for storing data in JSON files."""
    
    def __init__(self, file_path: str = "watertracker.json"):
        """
        Initialize data storage.
        
        Args:
            file_path: Path to JSON file.
        """
        self.file_path = file_path
        self.data: Dict[str, Any] = {
            "profile": None,
            "water_logs": [],
            "checksum": ""
        }
        
        # Load data from file if exists
        if os.path.exists(file_path):
            self.load()
    
    def _calculate_checksum(self, data_without_checksum: Dict[str, Any]) -> str:
        """
        Calculate SHA-256 checksum for data.
        
        Args:
            data_without_checksum: Data without checksum field.
            
        Returns:
            SHA-256 checksum string.
        """
        data_str = json.dumps(data_without_checksum, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _verify_checksum(self, data: Dict[str, Any]) -> bool:
        """
        Verify data checksum.
        
        Args:
            data: Data with checksum.
            
        Returns:
            True if checksum matches, False otherwise.
        """
        expected_checksum = data.get("checksum", "")
        data_copy = data.copy()
        data_copy.pop("checksum", None)
        actual_checksum = self._calculate_checksum(data_copy)
        
        return expected_checksum == actual_checksum
    
    def load(self) -> bool:
        """
        Load data from JSON file.
        
        Returns:
            True if data loaded successfully, False otherwise.
        """
        try:
            with open(self.file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Verify checksum
            if not self._verify_checksum(loaded_data):
                logger.warning("Checksum mismatch.")
                return False
            
            self.data = loaded_data
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save data to JSON file.
        
        Returns:
            True if data saved successfully, False otherwise.
        """
        try:
            # Create data copy without checksum
            data_copy = self.data.copy()
            data_copy.pop("checksum", None)
            
            # Calculate new checksum
            checksum = self._calculate_checksum(data_copy)
            
            # Add checksum and save
            self.data["checksum"] = checksum
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
            
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def export_data(self, export_path: str) -> bool:
        """
        Export data to JSON file.
        
        Args:
            export_path: Path to export file.
            
        Returns:
            True if data exported successfully, False otherwise.
        """
        try:
            # Create data copy
            export_data = self.data.copy()
            
            # Add export metadata
            export_data["export_date"] = time.time()
            
            # Calculate new checksum
            data_without_checksum = export_data.copy()
            data_without_checksum.pop("checksum", None)
            checksum = self._calculate_checksum(data_without_checksum)
            export_data["checksum"] = checksum
            
            # Save to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False
    
    def import_data(self, import_path: str) -> bool:
        """
        Import data from JSON file.
        
        Args:
            import_path: Path to import file.
            
        Returns:
            True if data imported successfully, False otherwise.
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            # Verify checksum
            if not self._verify_checksum(import_data):
                logger.warning("Checksum mismatch.")
                return False
            
            # Update data
            self.data = import_data
            
            # Save updated data
            return self.save()
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
    
    def save_profile(self, profile: Profile) -> bool:
        """
        Save user profile.
        
        Args:
            profile: User profile object.
            
        Returns:
            True if profile saved successfully, False otherwise.
        """
        try:
            # Convert profile to dictionary
            profile_dict = {
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "age_years": profile.age_years,
                "gender": profile.gender.name
            }
            
            self.data["profile"] = profile_dict
            return self.save()
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def load_profile(self) -> Optional[Profile]:
        """
        Load user profile.
        
        Returns:
            User profile object or None if profile not found.
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
            logger.error(f"Error loading profile: {e}")
            return None
    
    def add_water_log(self, water_log: WaterLog) -> bool:
        """
        Add water consumption record.
        
        Args:
            water_log: Water consumption record object.
            
        Returns:
            True if record added successfully, False otherwise.
        """
        try:
            # Convert record to dictionary
            log_dict = {
                "amount_ml": water_log.amount_ml,
                "timestamp": water_log.timestamp,
                "note": water_log.note
            }
            
            self.data["water_logs"].append(log_dict)
            return self.save()
        except Exception as e:
            logger.error(f"Error adding water consumption record: {e}")
            return False
    
    def update_water_log(self, index: int, water_log: WaterLog) -> bool:
        """
        Update water consumption record.
        
        Args:
            index: Record index.
            water_log: Updated record object.
            
        Returns:
            True if record updated successfully, False otherwise.
        """
        try:
            if 0 <= index < len(self.data["water_logs"]):
                # Convert record to dictionary
                log_dict = {
                    "amount_ml": water_log.amount_ml,
                    "timestamp": water_log.timestamp,
                    "note": water_log.note
                }
                
                self.data["water_logs"][index] = log_dict
                return self.save()
            else:
                logger.warning(f"Error: Index {index} out of range.")
                return False
        except Exception as e:
            logger.error(f"Error updating water consumption record: {e}")
            return False
    
    def delete_water_log(self, index: int) -> bool:
        """
        Delete water consumption record.
        
        Args:
            index: Record index.
            
        Returns:
            True if record deleted successfully, False otherwise.
        """
        try:
            if 0 <= index < len(self.data["water_logs"]):
                del self.data["water_logs"][index]
                return self.save()
            else:
                logger.warning(f"Error: Index {index} out of range.")
                return False
        except Exception as e:
            logger.error(f"Error deleting water consumption record: {e}")
            return False
    
    def get_water_logs(self, start_time: Optional[float] = None, 
                      end_time: Optional[float] = None) -> List[Tuple[int, WaterLog]]:
        """
        Get water consumption records list for specified period.
        
        Args:
            start_time: Period start (Unix timestamp).
            end_time: Period end (Unix timestamp).
            
        Returns:
            List of tuples (index, record) for water consumption.
        """
        logs = []
        
        for i, log_dict in enumerate(self.data.get("water_logs", [])):
            timestamp = log_dict.get("timestamp", 0)
            
            # Verify if record is in specified period
            if ((start_time is None or timestamp >= start_time) and 
                (end_time is None or timestamp <= end_time)):
                
                log = WaterLog(
                    amount_ml=log_dict.get("amount_ml", 0),
                    timestamp=timestamp,
                    note=log_dict.get("note")
                )
                
                logs.append((i, log))
        
        return logs
    
    def clear_all_data(self) -> bool:
        """
        Clear all data and return storage to initial state.
        
        Returns:
            True if data cleared successfully, False otherwise.
        """
        try:
            # Reset data to initial state
            self.data = {
                "profile": None,
                "water_logs": [],
                "checksum": ""
            }
            
            # Save updated data
            return self.save()
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False 