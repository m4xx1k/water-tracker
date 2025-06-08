
import pytest
from unittest.mock import MagicMock
from model.profile import Profile, Gender
from repository.data_store import DataStore
from services.profile_service import ProfileService


@pytest.fixture
def mock_data_store():
    data_store = MagicMock(spec=DataStore)
    
    # Налаштування поведінки моку
    data_store.load_profile.return_value = Profile(
        height_cm=180,
        weight_kg=80.0,
        age_years=30,
        gender=Gender.MALE
    )
    
    data_store.save_profile.return_value = True
    
    return data_store


def test_get_profile(mock_data_store):
    profile_service = ProfileService(mock_data_store)
    
    profile = profile_service.get_profile()
    assert profile is not None
    assert profile.height_cm == 180
    assert profile.weight_kg == 80.0
    assert profile.age_years == 30
    assert profile.gender == Gender.MALE
    
    mock_data_store.load_profile.assert_called_once()


def test_get_profile_not_found(mock_data_store):
    """Тест отримання профілю, коли він не знайдений."""
    # Зміна поведінки моку
    mock_data_store.load_profile.return_value = None
    
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Перевірка, що повертається None
    assert profile_service.get_profile() is None


def test_create_profile(mock_data_store):
    """Тест створення профілю користувача."""
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Створення профілю
    profile = profile_service.create_profile(
        height_cm=170,
        weight_kg=70.0,
        age_years=25,
        gender="FEMALE"
    )
    
    # Перевірка створеного профілю
    assert profile is not None
    assert profile.height_cm == 170
    assert profile.weight_kg == 70.0
    assert profile.age_years == 25
    assert profile.gender == Gender.FEMALE
    
    # Перевірка виклику методу сховища
    mock_data_store.save_profile.assert_called_once()


def test_create_profile_invalid_data(mock_data_store):
    """Тест створення профілю з недійсними даними."""
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Перевірка валідації висоти
    with pytest.raises(ValueError):
        profile_service.create_profile(
            height_cm=0,
            weight_kg=70.0,
            age_years=25,
            gender="FEMALE"
        )
    
    # Перевірка валідації ваги
    with pytest.raises(ValueError):
        profile_service.create_profile(
            height_cm=170,
            weight_kg=0,
            age_years=25,
            gender="FEMALE"
        )
    
    # Перевірка валідації віку
    with pytest.raises(ValueError):
        profile_service.create_profile(
            height_cm=170,
            weight_kg=70.0,
            age_years=0,
            gender="FEMALE"
        )
    
    # Перевірка валідації статі
    with pytest.raises(ValueError):
        profile_service.create_profile(
            height_cm=170,
            weight_kg=70.0,
            age_years=25,
            gender="INVALID"
        )


def test_update_profile(mock_data_store):
    """Тест оновлення профілю користувача."""
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Оновлення профілю
    profile = profile_service.update_profile(
        height_cm=175,
        weight_kg=75.0,
        age_years=35,
        gender="OTHER"
    )
    
    # Перевірка оновленого профілю
    assert profile is not None
    assert profile.height_cm == 175
    assert profile.weight_kg == 75.0
    assert profile.age_years == 35
    assert profile.gender == Gender.OTHER
    
    # Перевірка виклику методу сховища
    mock_data_store.save_profile.assert_called_once()


def test_has_profile(mock_data_store):
    """Тест перевірки наявності профілю користувача."""
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Перевірка, що профіль існує
    assert profile_service.has_profile() is True
    
    # Зміна поведінки моку
    mock_data_store.load_profile.return_value = None
    
    # Перевірка, що профіль не існує
    assert profile_service.has_profile() is False


def test_get_daily_target(mock_data_store):
    """Тест отримання денної норми води."""
    # Створення сервісу з моком сховища
    profile_service = ProfileService(mock_data_store)
    
    # Отримання денної норми
    daily_target = profile_service.get_daily_target()
    
    # Перевірка, що денна норма відповідає профілю
    expected_target = profile_service.get_profile().daily_target_ml
    assert daily_target == expected_target 