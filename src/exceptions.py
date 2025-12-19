class WeatherAPIError(Exception):
    pass

class InvalidAPIKeyError(WeatherAPIError):
    pass

class CityNotFoundError(WeatherAPIError):
    pass
