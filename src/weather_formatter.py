from typing import Dict, List
from datetime import datetime

WEATHER_EMOJIS = {
    'ясно': '☀️', 'солнечно': '☀️', 'clear': '☀️',
    'пасмурно': '☁️', 'облачно': '⛅', 'тучи': '☁️',
    'дождь': '🌧️', 'ливень': '🌧️', 'rain': '🌧️',
    'снег': '❄️', 'снегопад': '❄️', 'snow': '❄️',
    'туман': '🌫️', 'fog': '🌫️', 'mist': '🌫️',
    'гроза': '⛈️', 'thunderstorm': '⛈️',
    'местами дождь': '🌦️', 'небольшой дождь': '🌦️'
}


def format_weather_output(weather_data: Dict, city: str) -> str:
    try:
        temp = weather_data['main']['temp']
        feels_like = weather_data['main'].get('feels_like', temp)
        description = weather_data['weather'][0]['description'].lower()
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']

        emoji = '🌤️'
        for key, value in WEATHER_EMOJIS.items():
            if key in description:
                emoji = value
                break

        return (f"{emoji} *Погода в {city}:*\n"
                f"🌡️ Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
                f"📝 {description.capitalize()}\n"
                f"💧 Влажность: {humidity}%\n"
                f"📊 Давление: {pressure} гПа\n"
                f"💨 Ветер: {wind_speed} м/с")
    except KeyError as e:
        return f"⚠️ Неполные данные о погоде: отсутствует поле {e}"


def format_forecast_day(forecast_data: Dict, day_index: int) -> str:
    """Форматирует прогноз на один день"""
    try:
        # Группируем по дням
        forecasts_by_day = {}
        for item in forecast_data['list']:
            date = item['dt_txt'].split()[0]  # Берем только дату
            if date not in forecasts_by_day:
                forecasts_by_day[date] = []
            forecasts_by_day[date].append(item)

        days = list(forecasts_by_day.keys())
        if day_index >= len(days):
            return "❌ Неверный индекс дня"

        day = days[day_index]
        day_forecasts = forecasts_by_day[day]

        # Находим мин/макс температуру
        temps = [f['main']['temp'] for f in day_forecasts]
        min_temp = min(temps)
        max_temp = max(temps)

        # Берем наиболее частую погоду
        weather_counts = {}
        for f in day_forecasts:
            desc = f['weather'][0]['description']
            weather_counts[desc] = weather_counts.get(desc, 0) + 1

        common_weather = max(weather_counts.items(), key=lambda x: x[1])[0]

        emoji = '🌤️'
        for key, value in WEATHER_EMOJIS.items():
            if key in common_weather.lower():
                emoji = value
                break

        date_obj = datetime.strptime(day, "%Y-%m-%d")
        day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][date_obj.weekday()]

        return (f"{emoji} *{day_name}, {date_obj.strftime('%d.%m')}:*\n"
                f"🌡️ Температура: от {min_temp:.1f}°C до {max_temp:.1f}°C\n"
                f"📝 {common_weather.capitalize()}\n"
                f"📊 Прогнозов на день: {len(day_forecasts)}")
    except Exception as e:
        return f"⚠️ Ошибка форматирования прогноза: {e}"


def format_forecast_summary(forecast_data: Dict) -> str:
    """Краткое описание прогноза на 5 дней"""
    try:
        city = forecast_data['city']['name']
        country = forecast_data['city']['country']
        cnt = forecast_data['cnt']

        return (f"📅 *Прогноз на 5 дней для {city}, {country}:*\n"
                f"📊 Всего прогнозов: {cnt}\n"
                f"⏱️ Шаг прогноза: 3 часа\n\n"
                f"Выберите день для подробной информации:")
    except KeyError as e:
        return f"⚠️ Неполные данные прогноза: {e}"


def format_air_quality_report(analysis_result: Dict) -> str:
    status_emojis = {
        1: '✅', 2: '⚠️', 3: '🔶', 4: '❌', 5: '💀'
    }

    emoji = status_emojis.get(analysis_result['overall_index'], '❓')

    lines = [
        f"{emoji} *Качество воздуха: {analysis_result['overall_status']}*",
        f"📊 Индекс: {analysis_result['overall_index']}/5",
        ""
    ]

    for detail in analysis_result['details'][:6]:
        if detail['index']:
            comp_emoji = status_emojis.get(detail['index'], '📊')
            lines.append(
                f"{comp_emoji} {detail['name']}: "
                f"{detail['value']:.1f} {detail['unit']} "
                f"({detail['status']})"
            )

    if len(analysis_result['details']) > 6:
        lines.append(f"\nℹ️ Всего проанализировано {analysis_result['components_analyzed']} показателей")

    return "\n".join(lines)


def format_city_comparison(city1: str, weather1: Dict, city2: str, weather2: Dict) -> str:
    try:
        temp1 = weather1['main']['temp']
        temp2 = weather2['main']['temp']
        desc1 = weather1['weather'][0]['description']
        desc2 = weather2['weather'][0]['description']
        hum1 = weather1['main']['humidity']
        hum2 = weather2['main']['humidity']
        wind1 = weather1['wind']['speed']
        wind2 = weather2['wind']['speed']

        temp_diff = temp1 - temp2
        if temp_diff > 0:
            temp_comment = f"В {city1} на {temp_diff:.1f}°C теплее"
        elif temp_diff < 0:
            temp_comment = f"В {city2} на {abs(temp_diff):.1f}°C теплее"
        else:
            temp_comment = "Температура одинаковая"

        return (f"🌡️ *Сравнение погоды:*\n\n"
                f"🏙️ *{city1}:*\n"
                f"  Температура: {temp1:.1f}°C\n"
                f"  Погода: {desc1.capitalize()}\n"
                f"  Влажность: {hum1}%\n"
                f"  Ветер: {wind1} м/с\n\n"
                f"🏙️ *{city2}:*\n"
                f"  Температура: {temp2:.1f}°C\n"
                f"  Погода: {desc2.capitalize()}\n"
                f"  Влажность: {hum2}%\n"
                f"  Ветер: {wind2} м/с\n\n"
                f"📊 *Итог:* {temp_comment}")
    except KeyError as e:
        return f"⚠️ Ошибка сравнения: {e}"
