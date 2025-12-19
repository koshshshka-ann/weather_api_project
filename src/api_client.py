# Импорты внутри src/ делаются через точку
from .exceptions import WeatherAPIError, InvalidAPIKeyError, CityNotFoundError
from .cache_manager import CacheManager

# Остальные импорты как раньше
import json
import time
import requests
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Константы
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # секунды


class WeatherAPIClient:
    def __init__(self, api_key: str = None, cache_manager: CacheManager = None):
        self.api_key = api_key or API_KEY
        self.cache_manager = cache_manager or CacheManager()

    def make_request_with_retry(self, url: str, max_retries: int = MAX_RETRIES) -> requests.Response:
        """Выполняет HTTP-запрос с экспоненциальной задержкой при ошибках."""
        # Ваш код функции make_request_with_retry здесь
        pass

    def get_coordinates(self, city: str) -> Tuple[float, float]:
        """Получает координаты города через Geocoding API."""
        # Ваш код функции get_coordinates здесь
        pass

    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Получает погоду по координатам через Current Weather API."""
        # Ваш код функции get_weather_by_coordinates здесь
        pass

    # Добавьте новые методы из урока:
    def get_forecast_5d3h(self, lat: float, lon: float) -> list[dict]:
        """Прогноз на 5 дней с шагом 3 часа."""
        pass

    def get_air_pollution(self, lat: float, lon: float) -> dict:
        """Данные о загрязнении воздуха."""
        pass

    def analyze_air_pollution(self, components: dict, extended: bool = False) -> dict:
        """Анализ качества воздуха с выводом на русском."""
        pass
