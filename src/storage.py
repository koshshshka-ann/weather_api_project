import json
import os
from typing import Dict, Any

USER_DATA_FILE = "User_Data.json"


def load_all_users() -> Dict[str, Any]:
    """Загружает всех пользователей из файла."""
    if not os.path.exists(USER_DATA_FILE):
        return {}

    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"⚠️ Ошибка загрузки данных пользователей: {e}")
        return {}


def save_all_users(users_data: Dict[str, Any]) -> None:
    """Сохраняет всех пользователей в файл."""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"⚠️ Ошибка сохранения данных пользователей: {e}")


def load_user(user_id: int) -> Dict[str, Any]:
    """Загружает данные конкретного пользователя."""
    users = load_all_users()
    return users.get(str(user_id), {})


def save_user(user_id: int, user_data: Dict[str, Any]) -> None:
    """Сохраняет данные конкретного пользователя."""
    users = load_all_users()
    users[str(user_id)] = user_data
    save_all_users(users)
