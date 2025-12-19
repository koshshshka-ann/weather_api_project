#!/usr/bin/env python3
"""
Главный CLI интерфейс для погоды.
"""
import os
import sys
from pathlib import Path

# Решаем проблему импортов - добавляем src в путь
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"

# Проверяем существование src
if not src_dir.exists():
    print(f"❌ Папка {src_dir} не найдена!")
    print("Создайте папку src/ и переместите туда все модули")
    sys.exit(1)

# Добавляем src в Python path
sys.path.insert(0, str(src_dir))

print(f"📁 Текущая папка: {current_dir}")
print(f"📁 Папка src: {src_dir}")
print(f"✅ src существует: {src_dir.exists()}")

if src_dir.exists():
    print("📋 Содержимое src/:")
    for item in src_dir.iterdir():
        print(f"  - {item.name}")

# Теперь пробуем импортировать
try:
    # Импортируем из src (теперь они в sys.path)
    from dotenv import load_dotenv
    from api_client import WeatherAPIClient
    from cache_manager import CacheManager
    from weather_formatter import (
        format_weather_output, format_forecast_summary,
        format_forecast_day, format_air_quality_report,
        format_city_comparison
    )
    from storage import init_user_data
    from exceptions import WeatherAPIError, CityNotFoundError

    print("✅ Все модули успешно импортированы!")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nПроверьте:")
    print("1. Все ли файлы в папке src/ ?")
    print("2. Есть ли __init__.py в src/ ?")
    print("3. Запустите python -c \"import sys; print('\\n'.join(sys.path))\"")
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

        except CityNotFoundError:
            print(f"❌ Город '{city}' не найден")
        except WeatherAPIError as e:
            print(f"❌ Ошибка API: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")

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
        for i in range(min(5, len(forecast_data['list']) // 8)):
            day_forecast = format_forecast_day(forecast_data, i)
            print(f"\n{day_forecast}")

    except CityNotFoundError:
        print(f"❌ Город '{city}' не найден")
    except WeatherAPIError as e:
        print(f"❌ Ошибка API: {e}")
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

    except CityNotFoundError as e:
        print(f"❌ Город не найден: {e}")
    except WeatherAPIError as e:
        print(f"❌ Ошибка API: {e}")
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

    except CityNotFoundError:
        print(f"❌ Город '{city}' не найден")
    except WeatherAPIError as e:
        print(f"❌ Ошибка API: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


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

    except CityNotFoundError:
        print(f"❌ Тестовый город '{test_city}' не найден")
    except WeatherAPIError as e:
        print(f"❌ Ошибка API: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


def main():
    """Главная функция CLI"""
    # Загружаем переменные окружения
    load_dotenv()

    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        print("❌ ОШИБКА: API-ключ не найден!")
        print("Добавьте в файл .env строку:")
        print("OPENWEATHER_API_KEY=ваш_ключ_от_openweather")
        print("\nПолучить ключ можно на: https://openweathermap.org/api")
        return

    try:
        # Инициализируем данные пользователей
        init_user_data()

        # Создаем клиент
        cache_manager = CacheManager()
        api_client = WeatherAPIClient(API_KEY, cache_manager)

        print("✅ Погодный клиент инициализирован")

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

    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
