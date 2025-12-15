"""
Модуль для работы с API погоды OpenWeatherMap.
Включает кэширование, обработку ошибок и троттлинг.
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Константы
CACHE_FILE = "weather_cache.json"
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # секунды
CACHE_TTL_HOURS = 3


class WeatherAPIError(Exception):
    """Базовое исключение для ошибок API погоды."""
    pass


class InvalidAPIKeyError(WeatherAPIError):
    """Ошибка невалидного API-ключа."""
    pass


class CityNotFoundError(WeatherAPIError):
    """Ошибка города не найден."""
    pass


def make_request_with_retry(url: str, max_retries: int = MAX_RETRIES) -> requests.Response:
    """
    Выполняет HTTP-запрос с экспоненциальной задержкой при ошибках.

    Args:
        url: URL для запроса
        max_retries: Максимальное количество попыток

    Returns:
        Response объект

    Raises:
        WeatherAPIError: При превышении лимита попыток
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)

            # 429 - Too Many Requests (троттлинг)
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    print(f"⚠️  Превышен лимит запросов. Ждём {delay} сек... (попытка {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    raise WeatherAPIError("Превышен лимит запросов к API. Попробуйте позже.")

            return response

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                print(f"⚠️  Таймаут. Ждём {delay} сек... (попытка {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise WeatherAPIError("Сервер не отвечает. Проверьте соединение.")

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                print(f"⚠️  Ошибка соединения. Ждём {delay} сек... (попытка {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise WeatherAPIError("Ошибка соединения с сервером.")

    raise WeatherAPIError("Не удалось выполнить запрос после всех попыток.")


def get_coordinates(city: str) -> Tuple[float, float]:
    """
    Получает координаты города через Geocoding API.

    Args:
        city: Название города

    Returns:
        Кортеж (широта, долгота)

    Raises:
        CityNotFoundError: Город не найден
        InvalidAPIKeyError: Неверный API-ключ
        WeatherAPIError: Другие ошибки API
    """
    if not API_KEY:
        raise InvalidAPIKeyError("API-ключ не найден. Проверьте файл .env")

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&lang=ru&appid={API_KEY}"

    try:
        response = make_request_with_retry(url)

        if response.status_code == 401:
            raise InvalidAPIKeyError("Неверный API-ключ. Проверьте ключ в .env")
        elif response.status_code != 200:
            raise WeatherAPIError(f"Ошибка API: {response.status_code} - {response.reason}")

        data = response.json()

        if not data:
            raise CityNotFoundError(f"Город '{city}' не найден.")

        return data[0]['lat'], data[0]['lon']

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        raise WeatherAPIError(f"Ошибка при получении координат: {str(e)}")


def get_weather_by_coordinates(lat: float, lon: float) -> Dict:
    """
    Получает погоду по координатам через Current Weather API.

    Args:
        lat: Широта
        lon: Долгота

    Returns:
        Словарь с данными о погоде

    Raises:
        WeatherAPIError: Ошибки API
    """
    if not API_KEY:
        raise InvalidAPIKeyError("API-ключ не найден. Проверьте файл .env")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=ru&appid={API_KEY}"

    try:
        response = make_request_with_retry(url)

        if response.status_code == 401:
            raise InvalidAPIKeyError("Неверный API-ключ. Проверьте ключ в .env")
        elif response.status_code != 200:
            raise WeatherAPIError(f"Ошибка API: {response.status_code} - {response.reason}")

        return response.json()

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        raise WeatherAPIError(f"Ошибка при получении погоды: {str(e)}")


def save_to_cache(city: str, lat: float, lon: float, weather_data: Dict) -> None:
    """
    Сохраняет данные о погоде в кэш.

    Args:
        city: Название города
        lat: Широта
        lon: Долгота
        weather_data: Данные о погоде
    """
    cache_entry = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "weather_data": weather_data,
        "fetched_at": datetime.now().isoformat()
    }

    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"⚠️  Не удалось сохранить кэш: {e}")


def read_from_cache() -> Optional[Dict]:
    """
    Читает данные из кэша.

    Returns:
        Словарь с кэшированными данными или None
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Проверяем срок годности кэша
        fetched_at = datetime.fromisoformat(cache_data['fetched_at'])
        if datetime.now() - fetched_at > timedelta(hours=CACHE_TTL_HOURS):
            print("ℹ️  Кэш устарел (больше 3 часов).")
            return None

        return cache_data

    except (IOError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Ошибка чтения кэша: {e}")
        return None


def format_weather_output(weather_data: Dict, city: str) -> str:
    """
    Форматирует данные о погоде в читаемую строку.

    Args:
        weather_data: Данные о погоде от API
        city: Название города

    Returns:
        Отформатированная строка
    """
    try:
        temp = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        # Добавляем эмодзи в зависимости от погоды
        weather_emojis = {
            'ясно': '☀️',
            'пасмурно': '☁️',
            'дождь': '🌧️',
            'снег': '❄️',
            'туман': '🌫️',
            'облачно': '⛅',
        }

        emoji = '🌤️'  # дефолтный
        for key, value in weather_emojis.items():
            if key in description.lower():
                emoji = value
                break

        return (f"{emoji} Погода в {city}: {temp:.1f}°C, {description.capitalize()}\n"
                f"   💧 Влажность: {humidity}% | 💨 Ветер: {wind_speed} м/с")

    except KeyError as e:
        return f"⚠️  Неполные данные о погоде: отсутствует поле {e}"


def get_current_weather(city: str = None, lat: float = None, lon: float = None) -> Dict:
    """
    Основная функция получения погоды.

    Args:
        city: Название города (приоритет)
        lat: Широта
        lon: Долгота

    Returns:
        Словарь с данными о погоде

    Raises:
        ValueError: Не указаны ни город, ни координаты
    """
    if city:
        print(f"📍 Получаем погоду для города: {city}")
        lat, lon = get_coordinates(city)
    elif lat is not None and lon is not None:
        print(f"📍 Получаем погоду для координат: {lat}, {lon}")
        city = f"{lat:.4f}, {lon:.4f}"
    else:
        raise ValueError("Необходимо указать либо город, либо координаты")

    # Пробуем получить погоду
    try:
        weather_data = get_weather_by_coordinates(lat, lon)

        # Сохраняем в кэш
        if city and not (isinstance(city, str) and ',' in city):  # Не сохраняем сырые координаты
            save_to_cache(city, lat, lon, weather_data)

        return weather_data

    except WeatherAPIError as e:
        print(f"❌ Ошибка при запросе к API: {e}")

        # Предлагаем использовать кэш
        cache_data = read_from_cache()
        if cache_data and input("Использовать данные из кэша? (да/нет): ").lower() in ['да', 'yes', 'y', 'д']:
            print("📋 Используются кэшированные данные:")
            return cache_data['weather_data']
        else:
            raise


def run_cli():
    """
    Запускает интерфейс командной строки.
    """
    print("=" * 50)
    print("🌤️  ПРОГНОЗ ПОГОДЫ (OpenWeatherMap)")
    print("=" * 50)

    while True:
        print("\nРежимы ввода:")
        print("  1 - По названию города")
        print("  2 - По координатам (широта, долгота)")
        print("  0 - Выход")

        try:
            choice = input("\nВыберите режим (0-2): ").strip()

            if choice == '0':
                print("👋 До свидания!")
                break

            elif choice == '1':
                city = input("Введите название города: ").strip()
                if not city:
                    print("⚠️  Название города не может быть пустым.")
                    continue

                try:
                    weather_data = get_current_weather(city=city)
                    print("\n" + format_weather_output(weather_data, city))
                except WeatherAPIError as e:
                    print(f"❌ {e}")
                except Exception as e:
                    print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")

            elif choice == '2':
                try:
                    lat = float(input("Введите широту: ").replace(',', '.'))
                    lon = float(input("Введите долготу: ").replace(',', '.'))

                    weather_data = get_current_weather(lat=lat, lon=lon)
                    location = f"{lat:.4f}, {lon:.4f}"
                    print("\n" + format_weather_output(weather_data, location))
                except ValueError:
                    print("❌ Неверный формат координат. Используйте числа.")
                except WeatherAPIError as e:
                    print(f"❌ {e}")
                except Exception as e:
                    print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")

            else:
                print("❌ Неверный выбор. Попробуйте снова.")

        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем.")
            break


if __name__ == "__main__":
    # Проверяем наличие API-ключа
    if not API_KEY:
        print("❌ ОШИБКА: API-ключ не найден!")
        print("Добавьте в файл .env строку:")
        print("OPENWEATHER_API_KEY=ваш_ключ_от_openweather")
        print("\nПолучить ключ можно на: https://openweathermap.org/api")
    else:
        run_cli()
