
import os
import json
import tempfile
import pytest
from model.profile import Profile, Gender, WaterLog
from repository.data_store import DataStore


@pytest.fixture
def temp_data_file():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


def test_init_data_store():
    """Test data store initialization."""
    data_store = DataStore("nonexistent.json")
    assert data_store.data["profile"] is None
    assert data_store.data["water_logs"] == []
    assert data_store.data["checksum"] == ""


def test_save_and_load(temp_data_file):
    """Test saving and loading data."""
    # Create and save data
    data_store = DataStore(temp_data_file)
    data_store.data["profile"] = {"height_cm": 180, "weight_kg": 80.0, "age_years": 30, "gender": "MALE"}
    data_store.data["water_logs"] = [{"amount_ml": 250, "timestamp": 1622548800.0, "note": "Morning"}]
    
    # Check saving
    assert data_store.save() is True
    
    # Check if file is created
    assert os.path.exists(temp_data_file)

    # Завантаження даних в новий об'єкт
    data_store2 = DataStore(temp_data_file)
    assert data_store2.data["profile"] == {"height_cm": 180, "weight_kg": 80.0, "age_years": 30, "gender": "MALE"}
    assert len(data_store2.data["water_logs"]) == 1
    assert data_store2.data["water_logs"][0]["amount_ml"] == 250


def test_checksum_verification(temp_data_file):
    """Test checksum verification."""
    # Create and save data
    data_store = DataStore(temp_data_file)
    data_store.data["profile"] = {"height_cm": 180, "weight_kg": 80.0, "age_years": 30, "gender": "MALE"}
    data_store.save()
    
    # Load data
    data_store2 = DataStore(temp_data_file)
    assert data_store2.data["profile"] == {"height_cm": 180, "weight_kg": 80.0, "age_years": 30, "gender": "MALE"}
    
    # Corrupt checksum in file
    with open(temp_data_file, 'r') as f:
        data = json.load(f)
    
    data["checksum"] = "invalid_checksum"
    
    with open(temp_data_file, 'w') as f:
        json.dump(data, f)
    
    # Try to load data with invalid checksum
    data_store3 = DataStore(temp_data_file)
    assert data_store3.load() is False


def test_profile_operations(temp_data_file):
    """Тест операцій з профілем користувача."""
    data_store = DataStore(temp_data_file)
    
    # Create profile
    profile = Profile(
        height_cm=180,
        weight_kg=80.0,
        age_years=30,
        gender=Gender.MALE
    )
    
    assert data_store.save_profile(profile) is True
    
    loaded_profile = data_store.load_profile()
    assert loaded_profile is not None
    assert loaded_profile.height_cm == 180
    assert loaded_profile.weight_kg == 80.0
    assert loaded_profile.age_years == 30
    assert loaded_profile.gender == Gender.MALE


def test_water_log_operations(temp_data_file):
    """Test water log operations."""
    data_store = DataStore(temp_data_file)
    
    # Add log
    log1 = WaterLog(amount_ml=250, timestamp=1622548800.0, note="Morning")
    assert data_store.add_water_log(log1) is True
    
    # Add another log
    log2 = WaterLog(amount_ml=300, timestamp=1622552400.0, note="Afternoon")
    assert data_store.add_water_log(log2) is True
    
    # Get all logs
    logs = data_store.get_water_logs()
    assert len(logs) == 2
    
    # Check first log
    index1, log1_loaded = logs[0]
    assert index1 == 0
    assert log1_loaded.amount_ml == 250
    assert log1_loaded.timestamp == 1622548800.0
    assert log1_loaded.note == "Morning"
    
    # Update log
    updated_log = WaterLog(amount_ml=200, timestamp=1622548800.0, note="Updated note")
    assert data_store.update_water_log(0, updated_log) is True
    
    # Check updated log
    logs = data_store.get_water_logs()
    index, log = logs[0]
    assert log.amount_ml == 200
    assert log.note == "Updated note"
    
    # Delete log
    assert data_store.delete_water_log(0) is True
    
    # Check if log is deleted
    logs = data_store.get_water_logs()
    assert len(logs) == 1
    assert logs[0][0] == 0  # After deletion, indices are updated


def test_get_water_logs_by_period(temp_data_file):
    """Тест отримання записів за період."""
    data_store = DataStore(temp_data_file)
    
    # Add logs for different days
    log1 = WaterLog(amount_ml=250, timestamp=1622548800.0)  # 2021-06-01 12:00:00
    log2 = WaterLog(amount_ml=300, timestamp=1622635200.0)  # 2021-06-02 12:00:00
    log3 = WaterLog(amount_ml=350, timestamp=1622721600.0)  # 2021-06-03 12:00:00
    
    data_store.add_water_log(log1)
    data_store.add_water_log(log2)
    data_store.add_water_log(log3)
    
    # Get logs for specific period
    logs = data_store.get_water_logs(start_time=1622548800.0, end_time=1622635200.0)
    assert len(logs) == 2
    
    # Get logs only from start date
    logs = data_store.get_water_logs(start_time=1622635200.0)
    assert len(logs) == 2
    
    # Get logs only to end date
    logs = data_store.get_water_logs(end_time=1622635200.0)
    assert len(logs) == 2 