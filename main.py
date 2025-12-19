#!/usr/bin/env python3
"""
Главное CLI приложение для прогноза погоды.
Файл находится в корне проекта.
"""
import sys
import os
from pathlib import Path

# Добавляем папку src в путь Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Теперь импортируем из src
try:
    from api_client import WeatherAPIClient
    from cache_manager import CacheManager
    from exceptions import WeatherAPIError, InvalidAPIKeyError, CityNotFoundError
    from weather_formatter import format_weather_output
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Проверьте, что папка src/ существует и содержит все модули")
    sys.exit(1)


# ===== ВАШ СУЩЕСТВУЮЩИЙ КОД =====
# (сохраняем всю логику из вашего weather_app.py)

def get_current_weather(city: str = None, lat: float = None, lon: float = None):
    """Основная функция получения погоды (ваш существующий код)"""
    pass  # Замените на ваш код


def run_cli():
    """Запускает интерфейс командной строки (ваш существующий код)"""
    pass  # Замените на ваш код


def main():
    """Точка входа CLI приложения"""
    # Загружаем переменные окружения
    load_dotenv()

    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        print("❌ ОШИБКА: API-ключ не найден!")
        print("Добавьте в файл .env строку:")
        print("OPENWEATHER_API_KEY=ваш_ключ_от_openweather")
        print("\nПолучить ключ можно на: https://openweathermap.org/api")
        return

    try:
        # Инициализируем компоненты
        cache_manager = CacheManager()
        api_client = WeatherAPIClient(API_KEY, cache_manager)

        # Запускаем CLI
        run_cli()

    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
