# Water Tracker

Single-user water tracking application with ttkbootstrap-based GUI.

## Features

- Create/edit user profile
- Add/edit/delete water consumption records
- Status panel with progress percentage
- History view for selected period
- Data export/import to JSON with checksum (sha256)
- Reminders (optional)

## Requirements

- Python 3.10+
- ttkbootstrap

## Installation & Running

```bash
# Clone repository
git clone https://github.com/yourusername/water-tracker.git
cd water-tracker

# Install dependencies using uv
uv pip install -r requirements.txt

# Run application
python main.py
```

## Project Structure

- `model/` - Data model classes
- `services/` - Business logic
- `repository/` - Data storage handling
- `ui/` - User interface components
- `util/` - Helper functions
- `tests/` - Tests

## Testing

```bash
# Run tests with coverage
pytest --cov=.
```
