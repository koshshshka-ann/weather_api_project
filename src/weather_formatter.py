from typing import Dict


# Импорты не требуются, кроме стандартных типов

def format_weather_output(weather_data: Dict, city: str) -> str:
    """Форматирует данные о погоде в читаемую строку."""
    try:
        temp = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        weather_emojis = {
            'ясно': '☀️',
            'пасмурно': '☁️',
            'дождь': '🌧️',
            'снег': '❄️',
            'туман': '🌫️',
            'облачно': '⛅',
        }

        emoji = '🌤️'
        for key, value in weather_emojis.items():
            if key in description.lower():
                emoji = value
                break

        return (f"{emoji} Погода в {city}: {temp:.1f}°C, {description.capitalize()}\n"
                f"   💧 Влажность: {humidity}% | 💨 Ветер: {wind_speed} м/с")

    except KeyError as e:
        return f"⚠️ Неполные данные о погоде: отсутствует поле {e}"
