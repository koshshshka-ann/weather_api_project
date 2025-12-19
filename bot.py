#!/usr/bin/env python3
"""
Telegram-бот для прогноза погоды.
"""
import os
import sys
import logging
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем абсолютный путь к папке src
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"

# Диагностика перед импортами
logger.info(f"Текущая директория: {current_dir}")
logger.info(f"Папка src: {src_dir}")
logger.info(f"src существует: {src_dir.exists()}")

if src_dir.exists():
    logger.info("Содержимое src/:")
    for item in src_dir.iterdir():
        logger.info(f"  - {item.name}")

# Добавляем src в путь Python двумя способами для надежности
sys.path.insert(0, str(current_dir))  # Корень проекта
sys.path.insert(0, str(src_dir))  # Папка src

# Показываем путь Python
logger.info("Python sys.path:")
for i, path in enumerate(sys.path[:5]):  # Первые 5 путей
    logger.info(f"  [{i}] {path}")

try:
    # ВАЖНО: Пробуем импортировать через src.
    # Твой __init__.py делает модули доступными через 'from src import ...'
    from dotenv import load_dotenv
    import telebot
    from telebot import types

    # Способ 1: Импорт через src (использует твой __init__.py)
    try:
        logger.info("Пробую импорт через 'src'...")
        from src import (
            WeatherAPIClient, CacheManager,
            WeatherAPIError, CityNotFoundError,
            format_weather_output
        )
        # Отдельно импортируем функции из storage
        from src import load_user, save_user, load_all_users, save_all_users

        logger.info("✅ Успешный импорт через 'src'")

    except ImportError as e1:
        logger.warning(f"Импорт через 'src' не сработал: {e1}")

        # Способ 2: Прямой импорт (если src в sys.path)
        logger.info("Пробую прямой импорт...")
        from api_client import WeatherAPIClient
        from cache_manager import CacheManager
        from exceptions import WeatherAPIError, CityNotFoundError
        from weather_formatter import format_weather_output
        from storage import load_user, save_user, load_all_users, save_all_users

        logger.info("✅ Успешный прямой импорт")

    # Импортируем дополнительные функции из weather_formatter
    try:
        # Пробуем оба способа
        try:
            from src import (
                format_forecast_summary, format_forecast_day,
                format_air_quality_report, format_city_comparison
            )
        except ImportError:
            from weather_formatter import (
                format_forecast_summary, format_forecast_day,
                format_air_quality_report, format_city_comparison
            )
    except ImportError as e:
        logger.warning(f"Некоторые функции форматирования не импортированы: {e}")


        # Определим заглушки для недостающих функций
        def format_forecast_summary(data):
            return f"Прогноз для {data.get('city', {}).get('name', 'города')}"


        def format_forecast_day(data, day_idx):
            return f"Прогноз на день {day_idx + 1}"


        def format_air_quality_report(analysis):
            return f"Качество воздуха: {analysis.get('overall_status', 'Нет данных')}"


        def format_city_comparison(city1, weather1, city2, weather2):
            return f"Сравнение {city1} и {city2}"


    # Определяем дополнительные функции storage
    def update_user_location(user_id, city, lat, lon):
        """Обновляет локацию пользователя"""
        user_data = load_user(user_id)
        user_data["last_city"] = city
        user_data["last_lat"] = lat
        user_data["last_lon"] = lon
        save_user(user_id, user_data)


    def toggle_notifications(user_id, enabled=None):
        """Переключает уведомления"""
        user_data = load_user(user_id)
        if "notifications" not in user_data:
            user_data["notifications"] = {"enabled": False, "interval_h": 2}

        if enabled is None:
            user_data["notifications"]["enabled"] = not user_data["notifications"]["enabled"]
        else:
            user_data["notifications"]["enabled"] = enabled

        save_user(user_id, user_data)
        return user_data["notifications"]["enabled"]


    logger.info("✅ Все модули успешно импортированы")

except ImportError as e:
    logger.error(f"❌ Критическая ошибка импорта: {e}")
    logger.error("\nПопробуйте:")
    logger.error("1. Убедитесь, что все файлы в папке src/")
    logger.error("2. Проверьте наличие __init__.py в src/")
    logger.error("3. Запустите в корне проекта: python -c 'import sys; print(sys.path)'")

    # Детальная диагностика
    import traceback

    logger.error(f"\nТрейсбэк:\n{traceback.format_exc()}")

    sys.exit(1)

# Загружаем переменные окружения
load_dotenv()

# Получаем токены
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Проверяем токены
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден в .env файле")
    logger.error("Добавьте в .env: BOT_TOKEN=ваш_токен_бота")
    logger.error("Получите токен у @BotFather в Telegram")
    sys.exit(1)

if not API_KEY:
    logger.error("❌ OPENWEATHER_API_KEY не найден в .env файле")
    logger.error("Добавьте в .env: OPENWEATHER_API_KEY=ваш_ключ_от_openweather")
    logger.error("Получите ключ на https://openweathermap.org/api")
    sys.exit(1)

# Создаем экземпляры
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    cache_manager = CacheManager()
    weather_client = WeatherAPIClient(API_KEY, cache_manager)
    logger.info("✅ Клиенты инициализированы")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации: {e}")
    sys.exit(1)

# ===== КОМАНДЫ БОТА =====
# (Здесь продолжается остальной код бота, который ты уже видел)

def create_back_markup(additional_buttons=None):
    """Создает клавиатуру с кнопкой Назад и дополнительными кнопками"""
    markup = types.InlineKeyboardMarkup()

    if additional_buttons:
        for btn in additional_buttons:
            markup.add(btn)

    back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
    markup.add(back_button)

    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data = load_user(user_id)

    welcome_text = (
        "🌤️ *Добро пожаловать в Weather Bot!*\n\n"
        "Я помогу узнать погоду в любом городе.\n\n"
        "*Основные команды:*\n"
        "• /weather [город] - текущая погода\n"
        "• /forecast [город] - прогноз на 5 дней\n"
        "• /compare [город1] [город2] - сравнить города\n"
        "• /air [город] - качество воздуха\n"
        "• /notifications - уведомления\n"
        "• /location - отправить геолокацию\n\n"
        "Или просто напишите название города!"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🌤️ Текущая погода")
    btn2 = types.KeyboardButton("📅 Прогноз на 5 дней")
    btn3 = types.KeyboardButton("🏙️ Сравнить города")
    btn4 = types.KeyboardButton("🌬️ Качество воздуха")
    btn5 = types.KeyboardButton("📍 Отправить местоположение", request_location=True)
    btn6 = types.KeyboardButton("🔔 Уведомления")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, welcome_text,
                     parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🌤️ Текущая погода")
def ask_city_current(message):
    msg = bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(msg, process_city_current)


def process_city_current(message):
    city = message.text.strip()
    if not city:
        bot.send_message(message.chat.id, "❌ Город не указан")
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        weather_data = weather_client.get_current_weather(lat, lon)
        response = format_weather_output(weather_data, city)

        # Сохраняем локацию
        update_user_location(message.from_user.id, city, lat, lon)

        # Кнопка для дополнительной информации
        markup = types.InlineKeyboardMarkup()
        btn_air = types.InlineKeyboardButton("🌬️ Качество воздуха", callback_data=f"air_{city}")
        btn_forecast = types.InlineKeyboardButton("📅 Прогноз", callback_data=f"forecast_{city}")
        markup.add(btn_air, btn_forecast)

        bot.send_message(message.chat.id, response,
                         parse_mode="Markdown", reply_markup=markup)

    except CityNotFoundError:
        # Кнопка назад при ошибке
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Город '{city}' не найден",
                         reply_markup=markup)

    except WeatherAPIError as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}",
                         reply_markup=markup)

    except Exception as e:
        logger.error(f"Ошибка: {e}")

        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, "😔 Произошла ошибка",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📅 Прогноз на 5 дней")
def ask_city_forecast(message):
    msg = bot.send_message(message.chat.id, "Введите название города для прогноза:")
    bot.register_next_step_handler(msg, process_city_forecast)


def process_city_forecast(message):
    city = message.text.strip()
    if not city:
        bot.send_message(message.chat.id, "❌ Город не указан")
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        forecast_data = weather_client.get_forecast_5d3h(lat, lon)

        summary = format_forecast_summary(forecast_data)

        # Создаем inline-клавиатуру с днями
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for i in range(5):
            if i < len(forecast_data['list']) // 8:
                btn = types.InlineKeyboardButton(f"День {i + 1}", callback_data=f"day_{city}_{i}")
                buttons.append(btn)

        markup.add(*buttons)
        btn_back = types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        markup.add(btn_back)

        bot.send_message(message.chat.id, summary,
                         parse_mode="Markdown", reply_markup=markup)

    except CityNotFoundError:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Город '{city}' не найден",
                         reply_markup=markup)

    except WeatherAPIError as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Ошибка API: {str(e)}",
                         reply_markup=markup)

    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('day_'))
def handle_day_selection(call):
    try:
        _, city, day_idx = call.data.split('_')
        day_idx = int(day_idx)

        lat, lon = weather_client.get_coordinates(city)
        forecast_data = weather_client.get_forecast_5d3h(lat, lon)

        day_forecast = format_forecast_day(forecast_data, day_idx)

        # Улучшаем навигацию
        markup = types.InlineKeyboardMarkup(row_width=2)

        # Кнопки навигации по дням
        nav_buttons = []
        if day_idx > 0:
            nav_buttons.append(types.InlineKeyboardButton(
                "◀️ Предыдущий",
                callback_data=f"day_{city}_{day_idx - 1}"
            ))

        nav_buttons.append(types.InlineKeyboardButton(
            "📋 Сводка",
            callback_data=f"forecast_{city}"
        ))

        if day_idx < 4 and day_idx < (len(forecast_data['list']) // 8) - 1:
            nav_buttons.append(types.InlineKeyboardButton(
                "Следующий ▶️",
                callback_data=f"day_{city}_{day_idx + 1}"
            ))

        markup.add(*nav_buttons)
        markup.add(types.InlineKeyboardButton(
            "◀️ Назад в меню",
            callback_data="back_to_main"
        ))

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=day_forecast,
                              parse_mode="Markdown",
                              reply_markup=markup)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {str(e)}")


@bot.message_handler(func=lambda message: message.text == "🏙️ Сравнить города")
def ask_cities_compare(message):
    msg = bot.send_message(message.chat.id,
                           "Введите два города через запятую (например: Москва, Санкт-Петербург):")
    bot.register_next_step_handler(msg, process_cities_compare)


def process_cities_compare(message):
    cities = [c.strip() for c in message.text.split(',')]
    if len(cities) != 2:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, "❌ Введите ровно два города через запятую",
                         reply_markup=markup)
        return

    city1, city2 = cities

    try:
        bot.send_chat_action(message.chat.id, 'typing')

        # Получаем данные для первого города
        lat1, lon1 = weather_client.get_coordinates(city1)
        weather1 = weather_client.get_current_weather(lat1, lon1)

        # Получаем данные для второго города
        lat2, lon2 = weather_client.get_coordinates(city2)
        weather2 = weather_client.get_current_weather(lat2, lon2)

        response = format_city_comparison(city1, weather1, city2, weather2)

        # Добавляем кнопку "Назад"
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, response,
                         parse_mode="Markdown",
                         reply_markup=markup)

    except CityNotFoundError as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Город не найден: {str(e)}",
                         reply_markup=markup)

    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🌬️ Качество воздуха")
def ask_city_air(message):
    msg = bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(msg, process_city_air)


def process_city_air(message):
    city = message.text.strip()
    if not city:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, "❌ Город не указан",
                         reply_markup=markup)
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        components = weather_client.get_air_pollution(lat, lon)
        analysis = weather_client.analyze_air_pollution(components, extended=True)

        response = format_air_quality_report(analysis)

        # Добавляем кнопку "Назад"
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, response,
                         parse_mode="Markdown",
                         reply_markup=markup)

    except CityNotFoundError:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Город '{city}' не найден",
                         reply_markup=markup)

    except WeatherAPIError as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Ошибка API: {str(e)}",
                         reply_markup=markup)

    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🔔 Уведомления")
def handle_notifications(message):
    user_id = message.from_user.id
    user_data = load_user(user_id)

    notifications_enabled = user_data.get("notifications", {}).get("enabled", False)
    status = "включены" if notifications_enabled else "выключены"

    markup = types.InlineKeyboardMarkup()
    if notifications_enabled:
        btn = types.InlineKeyboardButton("🔕 Выключить уведомления", callback_data="notif_off")
    else:
        btn = types.InlineKeyboardButton("🔔 Включить уведомления", callback_data="notif_on")

    markup.add(btn)

    bot.send_message(message.chat.id,
                     f"📢 Уведомления сейчас *{status}*\n\n"
                     "Вы будете получать погоду каждые 2 часа",
                     parse_mode="Markdown",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('notif_'))
def handle_notification_toggle(call):
    user_id = call.from_user.id

    if call.data == "notif_on":
        enabled = toggle_notifications(user_id, True)
        status = "включены"
    else:
        enabled = toggle_notifications(user_id, False)
        status = "выключены"

    bot.answer_callback_query(call.id, f"Уведомления {status}")

    # Обновляем сообщение
    markup = types.InlineKeyboardMarkup()
    if enabled:
        btn = types.InlineKeyboardButton("🔕 Выключить уведомления", callback_data="notif_off")
    else:
        btn = types.InlineKeyboardButton("🔔 Включить уведомления", callback_data="notif_on")

    markup.add(btn)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"📢 Уведомления сейчас *{status}*\n\n"
                               "Вы будете получать погоду каждые 2 часа",
                          parse_mode="Markdown",
                          reply_markup=markup)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude

        try:
            bot.send_chat_action(message.chat.id, 'typing')
            weather_data = weather_client.get_current_weather(lat, lon)

            city = f"{lat:.4f}, {lon:.4f}"
            response = format_weather_output(weather_data, city)

            update_user_location(message.from_user.id, city, lat, lon)

            # Добавляем кнопки
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_main")
            markup.add(back_button)

            bot.send_message(message.chat.id, response,
                             parse_mode="Markdown",
                             reply_markup=markup)

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('air_'))
def handle_air_quality_callback(call):
    city = call.data[4:]  # Убираем "air_"

    try:
        bot.send_chat_action(call.message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        components = weather_client.get_air_pollution(lat, lon)
        analysis = weather_client.analyze_air_pollution(components, extended=True)

        response = format_air_quality_report(analysis)

        # Добавляем кнопку "Назад"
        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        markup.add(back_button)

        bot.send_message(call.message.chat.id, response,
                         parse_mode="Markdown",
                         reply_markup=markup)
        bot.answer_callback_query(call.id)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('forecast_'))
def handle_forecast_callback(call):
    city = call.data[9:]  # Убираем "forecast_"

    try:
        bot.send_chat_action(call.message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        forecast_data = weather_client.get_forecast_5d3h(lat, lon)

        summary = format_forecast_summary(forecast_data)

        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for i in range(5):
            if i < len(forecast_data['list']) // 8:
                btn = types.InlineKeyboardButton(f"День {i + 1}", callback_data=f"day_{city}_{i}")
                buttons.append(btn)

        markup.add(*buttons)
        btn_back = types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        markup.add(btn_back)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=summary,
                              parse_mode="Markdown",
                              reply_markup=markup)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def handle_back_to_main(call):
    welcome_text = (
        "🌤️ *Добро пожаловать в Weather Bot!*\n\n"
        "Выберите действие из меню или введите название города."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🌤️ Текущая погода")
    btn2 = types.KeyboardButton("📅 Прогноз на 5 дней")
    btn3 = types.KeyboardButton("🏙️ Сравнить города")
    btn4 = types.KeyboardButton("🌬️ Качество воздуха")
    btn5 = types.KeyboardButton("📍 Отправить местоположение", request_location=True)
    btn6 = types.KeyboardButton("🔔 Уведомления")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=welcome_text,
                          parse_mode="Markdown")
    bot.send_message(call.message.chat.id, "Главное меню:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    """Обработка простого текста с названием города"""
    city = message.text.strip()

    if not city:
        bot.send_message(message.chat.id, "Пожалуйста, введите название города.")
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        lat, lon = weather_client.get_coordinates(city)
        weather_data = weather_client.get_current_weather(lat, lon)
        response = format_weather_output(weather_data, city)

        update_user_location(message.from_user.id, city, lat, lon)

        markup = types.InlineKeyboardMarkup()
        btn_air = types.InlineKeyboardButton("🌬️ Качество воздуха", callback_data=f"air_{city}")
        btn_forecast = types.InlineKeyboardButton("📅 Прогноз", callback_data=f"forecast_{city}")
        markup.add(btn_air, btn_forecast)

        bot.send_message(message.chat.id, response,
                         parse_mode="Markdown", reply_markup=markup)

    except CityNotFoundError:
        bot.send_message(message.chat.id, f"❌ Город '{city}' не найден")
    except WeatherAPIError as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "😔 Произошла ошибка")


# ===== ЗАПУСК БОТА =====

def main():
    logger.info("=" * 50)
    logger.info("🤖 Запускаю Weather Telegram Bot...")
    logger.info(f"Бот: {BOT_TOKEN[:15]}...")
    logger.info(f"API ключ: {API_KEY[:10]}...")
    logger.info("=" * 50)

    try:
        bot.polling(none_stop=True, interval=2, timeout=30)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка бота: {e}")


if __name__ == "__main__":
    main()
