class WeatherAPIError(Exception):
    """Базовое исключение для ошибок API погоды."""
    pass

class InvalidAPIKeyError(WeatherAPIError):
    """Ошибка невалидного API-ключа."""
    pass

class CityNotFoundError(WeatherAPIError):
    """Ошибка города не найден."""
    pass

class ForecastError(WeatherAPIError):
    """Ошибка получения прогноза."""
    pass
