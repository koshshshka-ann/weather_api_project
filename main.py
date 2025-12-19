#!/usr/bin/env python3
"""
Главный CLI интерфейс для погоды.
"""
import sys
import os
from pathlib import Path

# Добавляем src в путь Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
    from api_client import WeatherAPIClient
    from cache_manager import CacheManager
    from weather_formatter import (
        format_weather_output, format_forecast_summary,
        format_forecast_day, format_air_quality_report,
        format_city_comparison
    )
    from storage import init_user_data
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)


def show_current_weather(api_client: WeatherAPIClient):
    """Показать текущую погоду"""
    print("\n" + "=" * 50)
    print("🌤️  ПОЛУЧЕНИЕ ТЕКУЩЕЙ ПОГОДЫ")
    print("=" * 50)

    choice = input("\n1 - По городу\n2 - По координатам\nВыберите (1/2): ").strip()

    if choice == '1':
        city = input("Введите название города: ").strip()
        if not city:
            print("❌ Город не указан")
            return

        try:
            print(f"🔍 Ищем город '{city}'...")
            lat, lon = api_client.get_coordinates(city)
            print(f"📍 Координаты: {lat:.4f}, {lon:.4f}")

            weather_data = api_client.get_current_weather(lat, lon)
            print("\n" + format_weather_output(weather_data, city))

            # Предлагаем дополнительные данные
            if input("\nПоказать качество воздуха? (да/нет): ").lower() in ['да', 'yes', 'y', 'д']:
                components = api_client.get_air_pollution(lat, lon)
                analysis = api_client.analyze_air_pollution(components, extended=True)
                print("\n" + format_air_quality_report(analysis))

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    elif choice == '2':
        try:
            lat = float(input("Введите широту: ").replace(',', '.'))
            lon = float(input("Введите долготу: ").replace(',', '.'))

            location = f"{lat:.4f}, {lon:.4f}"
            print(f"📍 Получаем погоду для координат: {location}")

            weather_data = api_client.get_current_weather(lat, lon)
            print("\n" + format_weather_output(weather_data, location))

        except ValueError:
            print("❌ Неверный формат координат")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    else:
        print("❌ Неверный выбор")


def show_forecast(api_client: WeatherAPIClient):
    """Показать прогноз на 5 дней"""
    print("\n" + "=" * 50)
    print("📅  ПРОГНОЗ ПОГОДЫ НА 5 ДНЕЙ")
    print("=" * 50)

    city = input("Введите название города: ").strip()
    if not city:
        print("❌ Город не указан")
        return

    try:
        print(f"🔍 Ищем город '{city}'...")
        lat, lon = api_client.get_coordinates(city)

        print("📊 Получаем прогноз...")
        forecast_data = api_client.get_forecast_5d3h(lat, lon)

        print("\n" + format_forecast_summary(forecast_data))

        # Показываем краткий прогноз по дням
        print("\n" + "-" * 30)
        for i in range(5):
            if i < len(forecast_data['list']) // 8:  # Примерно 8 прогнозов в день
                day_forecast = format_forecast_day(forecast_data, i)
                print(f"\n{day_forecast}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def compare_cities(api_client: WeatherAPIClient):
    """Сравнить погоду в двух городах"""
    print("\n" + "=" * 50)
    print("🏙️  СРАВНЕНИЕ ПОГОДЫ В ГОРОДАХ")
    print("=" * 50)

    city1 = input("Введите первый город: ").strip()
    city2 = input("Введите второй город: ").strip()

    if not city1 or not city2:
        print("❌ Оба города должны быть указаны")
        return

    try:
        print(f"🔍 Сравниваем '{city1}' и '{city2}'...")

        # Получаем координаты и погоду для первого города
        lat1, lon1 = api_client.get_coordinates(city1)
        weather1 = api_client.get_current_weather(lat1, lon1)

        # Получаем координаты и погоду для второго города
        lat2, lon2 = api_client.get_coordinates(city2)
        weather2 = api_client.get_current_weather(lat2, lon2)

        print("\n" + format_city_comparison(city1, weather1, city2, weather2))

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def show_air_quality(api_client: WeatherAPIClient):
    """Показать качество воздуха"""
    print("\n" + "=" * 50)
    print("🌬️  КАЧЕСТВО ВОЗДУХА")
    print("=" * 50)

    city = input("Введите название города: ").strip()
    if not city:
        print("❌ Город не указан")
        return

    try:
        print(f"🔍 Проверяем качество воздуха в '{city}'...")
        lat, lon = api_client.get_coordinates(city)

        print("📊 Получаем данные о загрязнении...")
        components = api_client.get_air_pollution(lat, lon)

        print("🔍 Анализируем компоненты...")
        analysis = api_client.analyze_air_pollution(components, extended=True)

        print("\n" + format_air_quality_report(analysis))

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    """Главная функция CLI"""
    load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        print("❌ ОШИБКА: API-ключ не найден!")
        print("Добавьте в файл .env строку: OPENWEATHER_API_KEY=ваш_ключ")
        return

    # Инициализируем данные пользователей
    init_user_data()

    # Создаем клиент
    cache_manager = CacheManager()
    api_client = WeatherAPIClient(API_KEY, cache_manager)

    while True:
        print("\n" + "=" * 50)
        print("🌤️  ГЛАВНОЕ МЕНЮ ПОГОДНОГО ПРИЛОЖЕНИЯ")
        print("=" * 50)
        print("1. Текущая погода")
        print("2. Прогноз на 5 дней")
        print("3. Сравнить города")
        print("4. Качество воздуха")
        print("5. Тест функций API")
        print("0. Выход")

        choice = input("\nВыберите действие (0-5): ").strip()

        if choice == '0':
            print("\n👋 До свидания!")
            break
        elif choice == '1':
            show_current_weather(api_client)
        elif choice == '2':
            show_forecast(api_client)
        elif choice == '3':
            compare_cities(api_client)
        elif choice == '4':
            show_air_quality(api_client)
        elif choice == '5':
            test_api_functions(api_client)
        else:
            print("❌ Неверный выбор")

        input("\nНажмите Enter для продолжения...")


def test_api_functions(api_client: WeatherAPIClient):
    """Тестирование всех функций API"""
    print("\n🧪 ТЕСТИРОВАНИЕ API ФУНКЦИЙ")
    print("=" * 30)

    test_city = "Москва"

    try:
        print(f"1. Получение координат для '{test_city}'...")
        lat, lon = api_client.get_coordinates(test_city)
        print(f"   ✅ Координаты: {lat:.4f}, {lon:.4f}")

        print(f"2. Получение текущей погоды...")
        weather = api_client.get_current_weather(lat, lon)
        print(f"   ✅ Температура: {weather['main']['temp']:.1f}°C")

        print(f"3. Получение прогноза на 5 дней...")
        forecast = api_client.get_forecast_5d3h(lat, lon)
        print(f"   ✅ Прогнозов получено: {forecast['cnt']}")

        print(f"4. Получение качества воздуха...")
        components = api_client.get_air_pollution(lat, lon)
        print(f"   ✅ Компонентов получено: {len(components)}")

        print(f"5. Анализ качества воздуха...")
        analysis = api_client.analyze_air_pollution(components)
        print(f"   ✅ Статус: {analysis['overall_status']}")

        print("\n✅ Все функции работают корректно!")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
