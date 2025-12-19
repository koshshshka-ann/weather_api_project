import json
import os
from typing import Dict, Any
from datetime import datetime

USER_DATA_FILE = "User_Data.json"


def init_user_data():
    """Создает файл с данными пользователей, если его нет"""
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_all_users() -> Dict[str, Any]:
    init_user_data()
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_all_users(users_data: Dict[str, Any]) -> None:
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"⚠️ Ошибка сохранения данных: {e}")


def load_user(user_id: int) -> Dict[str, Any]:
    users = load_all_users()
    return users.get(str(user_id), {
        "notifications": {"enabled": False, "interval_h": 2},
        "created_at": datetime.now().isoformat()
    })


def save_user(user_id: int, user_data: Dict[str, Any]) -> None:
    users = load_all_users()
    users[str(user_id)] = user_data
    save_all_users(users)


def update_user_location(user_id: int, city: str, lat: float, lon: float) -> None:
    user_data = load_user(user_id)
    user_data["last_city"] = city
    user_data["last_lat"] = lat
    user_data["last_lon"] = lon
    user_data["last_updated"] = datetime.now().isoformat()
    save_user(user_id, user_data)


def toggle_notifications(user_id: int, enabled: bool = None) -> bool:
    user_data = load_user(user_id)
    if "notifications" not in user_data:
        user_data["notifications"] = {"enabled": False, "interval_h": 2}

    if enabled is None:
        # Переключаем
        user_data["notifications"]["enabled"] = not user_data["notifications"]["enabled"]
    else:
        user_data["notifications"]["enabled"] = enabled

    save_user(user_id, user_data)
    return user_data["notifications"]["enabled"]
