"""
Tests for user profile model.
"""

import pytest
from model.profile import Profile, Gender


def test_gender_bonus():
    """Test bonus coefficient calculation for different genders."""
    assert Gender.MALE.get_bonus() == 0.25
    assert Gender.FEMALE.get_bonus() == 0.1
    assert Gender.OTHER.get_bonus() == 0.15


def test_daily_target_male():
    """Test daily water norm calculation for males."""
    profile = Profile(
        height_cm=180,
        weight_kg=80.0,
        age_years=30,
        gender=Gender.MALE
    )
    
    # Розрахунок очікуваного результату
    # ((0.035*w)+(0.002*h)-(0.0002*a)+gender_bonus)*1000
    expected = round(((0.035 * 80.0) + (0.002 * 180) - (0.0002 * 30) + 0.25) * 1000)
    
    assert profile.daily_target_ml == expected


def test_daily_target_female():
    """Тест розрахунку денної норми води для жінок."""
    profile = Profile(
        height_cm=165,
        weight_kg=60.0,
        age_years=25,
        gender=Gender.FEMALE
    )
    
    # Розрахунок очікуваного результату
    expected = round(((0.035 * 60.0) + (0.002 * 165) - (0.0002 * 25) + 0.1) * 1000)
    
    assert profile.daily_target_ml == expected


def test_daily_target_other():
    """Тест розрахунку денної норми води для іншої статі."""
    profile = Profile(
        height_cm=170,
        weight_kg=70.0,
        age_years=35,
        gender=Gender.OTHER
    )
    
    # Розрахунок очікуваного результату
    expected = round(((0.035 * 70.0) + (0.002 * 170) - (0.0002 * 35) + 0.15) * 1000)
    
    assert profile.daily_target_ml == expected 