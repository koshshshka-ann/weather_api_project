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
    """
    Детальный прогноз на день по часам (8 прогнозов с шагом 3 часа)

    Возвращает:
    📅 Вс, 21.12:
    ⏰ 00:00: 0.5°C, пасмурно
    ⏰ 03:00: 0.6°C, пасмурно
    ⏰ 06:00: 0.7°C, легкий дождь
    ...
    """
    try:
        # Группируем прогнозы по дням
        forecasts_by_day = {}
        for item in forecast_data['list']:
            date_str = item['dt_txt'].split()[0]  # Берем только дату
            if date_str not in forecasts_by_day:
                forecasts_by_day[date_str] = []
            forecasts_by_day[date_str].append(item)

        # Сортируем дни по дате
        days = sorted(list(forecasts_by_day.keys()))

        if day_index >= len(days):
            return "❌ Неверный индекс дня"

        target_day = days[day_index]
        day_forecasts = forecasts_by_day[target_day]

        # Сортируем прогнозы по времени внутри дня
        day_forecasts.sort(key=lambda x: x['dt_txt'])

        # Конвертируем дату в читаемый формат
        date_obj = datetime.strptime(target_day, "%Y-%m-%d")
        day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][date_obj.weekday()]
        date_formatted = date_obj.strftime("%d.%m")

        # Создаем заголовок
        lines = [f"📅 *{day_name}, {date_formatted}:*", ""]

        # Добавляем каждый прогноз по часам
        for forecast in day_forecasts:
            # Извлекаем время
            time_str = forecast['dt_txt'].split()[1]
            hour_min = time_str[:5]  # ЧЧ:ММ

            # Извлекаем данные
            temp = forecast['main']['temp']
            feels_like = forecast['main'].get('feels_like', temp)
            description = forecast['weather'][0]['description'].lower()

            # Эмодзи для времени суток
            hour = int(time_str[:2])
            if 6 <= hour < 12:
                time_emoji = "🌅"  # утро
            elif 12 <= hour < 18:
                time_emoji = "☀️"  # день
            elif 18 <= hour < 23:
                time_emoji = "🌇"  # вечер
            else:
                time_emoji = "🌙"  # ночь

            # Эмодзи для погоды
            weather_emoji = '🌤️'
            for key, value in WEATHER_EMOJIS.items():
                if key in description:
                    weather_emoji = value
                    break

            lines.append(
                f"{time_emoji} *{hour_min}:* "
                f"{weather_emoji} {temp:.1f}°C "
                f"(ощущается {feels_like:.1f}°C), "
                f"{description.capitalize()}"
            )

        # Добавляем статистику внизу
        temps = [f['main']['temp'] for f in day_forecasts]
        min_temp = min(temps)
        max_temp = max(temps)

        lines.append(f"\n📊 *Статистика дня:*")
        lines.append(f"   🌡️ Диапазон: {min_temp:.1f}°C — {max_temp:.1f}°C")
        lines.append(f"   📈 Прогнозов: {len(day_forecasts)}/8")

        return "\n".join(lines)

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
