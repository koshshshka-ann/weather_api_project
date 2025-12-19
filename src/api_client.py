import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

import requests
from dotenv import load_dotenv
import os

# Импорты ВНУТРИ src должны быть относительными (с точкой)
from exceptions import WeatherAPIError, InvalidAPIKeyError, CityNotFoundError
from cache_manager import CacheManager

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

MAX_RETRIES = 3
BASE_RETRY_DELAY = 1


class WeatherAPIClient:
    def __init__(self, api_key: str = None, cache_manager: CacheManager = None):
        self.api_key = api_key or API_KEY
        self.cache_manager = cache_manager or CacheManager()

    def make_request_with_retry(self, url: str, max_retries: int = MAX_RETRIES) -> requests.Response:
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = BASE_RETRY_DELAY * (2 ** attempt)
                        print(f"⚠️ Превышен лимит запросов. Ждём {delay} сек...")
                        time.sleep(delay)
                        continue
                    raise WeatherAPIError("Превышен лимит запросов")
                return response
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    print(f"⚠️ Таймаут. Ждём {delay} сек...")
                    time.sleep(delay)
                else:
                    raise WeatherAPIError("Сервер не отвечает")
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    print(f"⚠️ Ошибка соединения. Ждём {delay} сек...")
                    time.sleep(delay)
                else:
                    raise WeatherAPIError("Ошибка соединения")
        raise WeatherAPIError("Не удалось выполнить запрос")

    def get_coordinates(self, city: str) -> Tuple[float, float]:
        if not self.api_key:
            raise InvalidAPIKeyError("API-ключ не найден")

        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&lang=ru&appid={self.api_key}"

        try:
            response = self.make_request_with_retry(url)
            if response.status_code == 401:
                raise InvalidAPIKeyError("Неверный API-ключ")
            elif response.status_code != 200:
                raise WeatherAPIError(f"Ошибка API: {response.status_code}")

            data = response.json()
            if not data:
                raise CityNotFoundError(f"Город '{city}' не найден")

            return data[0]['lat'], data[0]['lon']
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WeatherAPIError(f"Ошибка при получении координат: {str(e)}")

    def get_current_weather(self, lat: float, lon: float) -> Dict:
        if not self.api_key:
            raise InvalidAPIKeyError("API-ключ не найден")

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=ru&appid={self.api_key}"

        try:
            response = self.make_request_with_retry(url)
            if response.status_code == 401:
                raise InvalidAPIKeyError("Неверный API-ключ")
            elif response.status_code != 200:
                raise WeatherAPIError(f"Ошибка API: {response.status_code}")

            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WeatherAPIError(f"Ошибка при получении погоды: {str(e)}")

    def get_forecast_5d3h(self, lat: float, lon: float) -> Dict:
        if not self.api_key:
            raise InvalidAPIKeyError("API-ключ не найден")

        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=ru&appid={self.api_key}"

        try:
            response = self.make_request_with_retry(url)
            if response.status_code == 401:
                raise InvalidAPIKeyError("Неверный API-ключ")
            elif response.status_code != 200:
                raise WeatherAPIError(f"Ошибка API прогноза: {response.status_code}")

            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WeatherAPIError(f"Ошибка при получении прогноза: {str(e)}")

    def get_air_pollution(self, lat: float, lon: float) -> Dict:
        if not self.api_key:
            raise InvalidAPIKeyError("API-ключ не найден")

        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.api_key}"

        try:
            response = self.make_request_with_retry(url)
            if response.status_code == 401:
                raise InvalidAPIKeyError("Неверный API-ключ")
            elif response.status_code != 200:
                raise WeatherAPIError(f"Ошибка API загрязнения: {response.status_code}")

            data = response.json()
            if 'list' in data and len(data['list']) > 0:
                return data['list'][0]['components']
            raise WeatherAPIError("Нет данных о загрязнении")
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WeatherAPIError(f"Ошибка при получении загрязнения: {str(e)}")

    def analyze_air_pollution(self, components: dict, extended: bool = False) -> dict:
        """
        Анализирует компоненты загрязнения воздуха и возвращает отчет.

        Args:
            components: Словарь с компонентами от API (в µg/m³)
            extended: Если True, возвращает детальный отчет по всем компонентам

        Returns:
            Словарь с отчетом: {
                'overall_status': 'Хорошо',
                'overall_index': 1,
                'details': [{'component': 'SO2', 'value': 15.0, 'status': 'Хорошо', 'index': 1}, ...]
            }
        """
        # Таблица качества воздуха (из твоего скриншота)
        AIR_QUALITY_STANDARDS = {
            'so2': {
                'ranges': [
                    (0, 20, 1, 'Хорошо'),
                    (20, 80, 2, 'Удовлетворительно'),
                    (80, 250, 3, 'Умеренно'),
                    (250, 350, 4, 'Плохо'),
                    (350, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Диоксид серы (SO₂)',
                'unit': 'µg/m³'
            },
            'no2': {
                'ranges': [
                    (0, 40, 1, 'Хорошо'),
                    (40, 70, 2, 'Удовлетворительно'),
                    (70, 150, 3, 'Умеренно'),
                    (150, 200, 4, 'Плохо'),
                    (200, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Диоксид азота (NO₂)',
                'unit': 'µg/m³'
            },
            'pm10': {
                'ranges': [
                    (0, 20, 1, 'Хорошо'),
                    (20, 50, 2, 'Удовлетворительно'),
                    (50, 100, 3, 'Умеренно'),
                    (100, 200, 4, 'Плохо'),
                    (200, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Частицы PM₁₀',
                'unit': 'µg/m³'
            },
            'pm2_5': {
                'ranges': [
                    (0, 10, 1, 'Хорошо'),
                    (10, 25, 2, 'Удовлетворительно'),
                    (25, 50, 3, 'Умеренно'),
                    (50, 75, 4, 'Плохо'),
                    (75, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Частицы PM₂.₅',
                'unit': 'µg/m³'
            },
            'o3': {
                'ranges': [
                    (0, 60, 1, 'Хорошо'),
                    (60, 100, 2, 'Удовлетворительно'),
                    (100, 140, 3, 'Умеренно'),
                    (140, 180, 4, 'Плохо'),
                    (180, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Озон (O₃)',
                'unit': 'µg/m³'
            },
            'co': {
                'ranges': [
                    (0, 4400, 1, 'Хорошо'),
                    (4400, 9400, 2, 'Удовлетворительно'),
                    (9400, 12400, 3, 'Умеренно'),
                    (12400, 15400, 4, 'Плохо'),
                    (15400, float('inf'), 5, 'Очень плохо')
                ],
                'name': 'Угарный газ (CO)',
                'unit': 'µg/m³'
            },
            # Дополнительные параметры (не влияют на общий индекс)
            'nh3': {
                'ranges': [(0.1, 200, None, 'В норме')],
                'name': 'Аммиак (NH₃)',
                'unit': 'µg/m³'
            },
            'no': {
                'ranges': [(0.1, 100, None, 'В норме')],
                'name': 'Оксид азота (NO)',
                'unit': 'µg/m³'
            }
        }

        def get_component_status(value: float, ranges: list):
            """Определяет статус компонента по значению."""
            for min_val, max_val, index, status in ranges:
                if min_val <= value < max_val:
                    return status, index
            # Если значение выше максимального
            return 'Очень плохо', 5

        # Основные компоненты, которые влияют на общий индекс
        # Приводим ключи к нижнему регистру для унификации
        components_lower = {k.lower(): v for k, v in components.items()}

        main_components = ['so2', 'no2', 'pm10', 'pm2_5', 'o3', 'co']

        details = []
        max_index = 0
        overall_status = "Хорошо"

        # Анализируем каждый компонент
        for comp_key in main_components:
            if comp_key in components_lower:
                value = components_lower[comp_key]
                comp_info = AIR_QUALITY_STANDARDS[comp_key]
                status, index = get_component_status(value, comp_info['ranges'])

                details.append({
                    'component': comp_key,
                    'name': comp_info['name'],
                    'value': value,
                    'unit': comp_info['unit'],
                    'status': status,
                    'index': index
                })

                # Общий индекс = максимальный из всех компонентов
                if index and index > max_index:
                    max_index = index
                    overall_status = status

        # Добавляем дополнительные компоненты при расширенном режиме
        if extended:
            for comp_key in ['nh3', 'no']:
                if comp_key in components_lower:
                    value = components_lower[comp_key]
                    comp_info = AIR_QUALITY_STANDARDS[comp_key]
                    status, _ = get_component_status(value, comp_info['ranges'])

                    details.append({
                        'component': comp_key,
                        'name': comp_info['name'],
                        'value': value,
                        'unit': comp_info['unit'],
                        'status': status,
                        'index': None
                    })

        # Сортируем детали по важности (сначала основные)
        details.sort(key=lambda x: (x['index'] is None, -x['index'] if x['index'] else 0))

        return {
            'overall_status': overall_status,
            'overall_index': max_index,
            'details': details,
            'components_analyzed': len([d for d in details if d['index'] is not None])
        }

# Тестовая функция
def test_client():
    """Тестирование клиента"""
    print("🧪 Тестируем WeatherAPIClient...")

    # Загружаем ключ
    load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        print("❌ API ключ не найден в .env")
        return

    client = WeatherAPIClient(API_KEY)

    try:
        # Тест Москвы
        print("📍 Получаем координаты Москвы...")
        lat, lon = client.get_coordinates("Москва")
        print(f"✅ Координаты: {lat:.4f}, {lon:.4f}")

        print("🌤️ Получаем погоду...")
        weather = client.get_current_weather(lat, lon)
        print(f"✅ Температура: {weather['main']['temp']:.1f}°C")

        print("📅 Получаем прогноз...")
        forecast = client.get_forecast_5d3h(lat, lon)
        print(f"✅ Прогнозов: {forecast['cnt']}")

        print("🌬️ Получаем качество воздуха...")
        components = client.get_air_pollution(lat, lon)
        print(f"✅ Компонентов: {len(components)}")

        print("\n🎉 Все тесты пройдены!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    test_client()
