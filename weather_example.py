"""
Пример выделения конкретных полей из JSON ответа
"""
from http_client import get


def get_weather_example() -> None:
    """
    Пример: получаем погоду и выводим только температуру

    Используем OpenWeatherMap API (нужен API ключ)
    Для демо используем mock данные
    """
    try:
        # Пример запроса к погодному API
        # В реальности нужно зарегистрироваться на openweathermap.org
        # и получить API ключ

        print("Пример работы с погодным API:")
        print("1. Делаем запрос")
        print("2. Получаем JSON")
        print("3. Извлекаем нужные поля")

        # Для демонстрации используем тестовый API
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 55.7558,
            'longitude': 37.6176,
            'current_weather': 'true'
        }

        data = get(url, params=params)

        # Извлекаем конкретные поля
        if 'current_weather' in data:
            current = data['current_weather']
            temperature = current.get('temperature')
            windspeed = current.get('windspeed')
            weathercode = current.get('weathercode')

            print(f"\n🌡️  Текущая температура: {temperature}°C")
            print(f"💨 Скорость ветра: {windspeed} км/ч")
            print(f"☁️  Код погоды: {weathercode}")

            # Расшифровка кода погоды (пример)
            weather_codes = {
                0: "Ясно ☀️",
                1: "Преимущественно ясно 🌤",
                2: "Переменная облачность ⛅",
                3: "Пасмурно ☁️"
            }

            if weathercode in weather_codes:
                print(f"📝 Описание: {weather_codes[weathercode]}")

    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    get_weather_example()
