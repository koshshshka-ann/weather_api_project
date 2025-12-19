#!/usr/bin/env python3
"""
Telegram-бот для прогноза погоды.
"""
import os
import sys
import logging
from pathlib import Path

# Добавляем папку src в путь Python (ТАК ЖЕ КАК В main.py!)
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Импортируем из src (ТАК ЖЕ КАК В main.py!)
    from dotenv import load_dotenv
    import telebot

    from api_client import WeatherAPIClient
    from cache_manager import CacheManager
    from storage import load_user, save_user
    from weather_formatter import format_weather_output
    from exceptions import WeatherAPIError, CityNotFoundError

    logger.info("✅ Все модули успешно импортированы")

except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
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
    sys.exit(1)

if not API_KEY:
    logger.error("❌ OPENWEATHER_API_KEY не найден в .env файле")
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


# ===== ОСНОВНЫЕ КОМАНДЫ БОТА =====

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команд /start и /help"""
    user_id = message.from_user.id

    # Создаем или загружаем данные пользователя
    user_data = load_user(user_id)
    if not user_data:
        user_data = {"first_visit": True, "notifications": {"enabled": False}}
        save_user(user_id, user_data)

    welcome_text = (
        "🌤️ *Добро пожаловать в Weather Bot!*\n\n"
        "Я помогу узнать погоду в любом городе.\n\n"
        "*Доступные команды:*\n"
        "• /start или /help - это меню\n"
        "• /weather [город] - погода в городе\n"
        "• /forecast [город] - прогноз на 5 дней\n"
        "• /compare [город1] [город2] - сравнить города\n"
        "• /location - отправить геолокацию\n"
        "• /notifications - управление уведомлениями\n\n"
        "Или просто напишите название города!"
    )

    bot.reply_to(message, welcome_text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def handle_city_request(message):
    """Обработка простых запросов с названием города"""
    city = message.text.strip()

    if not city:
        bot.reply_to(message, "Пожалуйста, введите название города.")
        return

    try:
        # Получаем координаты
        bot.send_message(message.chat.id, f"🔍 Ищу город '{city}'...")
        lat, lon = weather_client.get_coordinates(city)

        # Получаем погоду
        weather_data = weather_client.get_weather_by_coordinates(lat, lon)

        # Форматируем ответ
        response = format_weather_output(weather_data, city)
        bot.reply_to(message, response)

        # Сохраняем последний город пользователя
        user_id = message.from_user.id
        user_data = load_user(user_id)
        user_data["last_city"] = city
        user_data["last_lat"] = lat
        user_data["last_lon"] = lon
        save_user(user_id, user_data)

    except CityNotFoundError:
        bot.reply_to(message, f"❌ Город '{city}' не найден. Проверьте написание.")
    except WeatherAPIError as e:
        bot.reply_to(message, f"⚠️ Ошибка при получении данных: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        bot.reply_to(message, "😔 Произошла внутренняя ошибка. Попробуйте позже.")


# ===== ЗАПУСК БОТА =====

def main():
    """Основная функция запуска бота"""
    logger.info("=" * 50)
    logger.info("🤖 Запускаю Weather Telegram Bot...")
    logger.info(f"Токен бота: {'*' * 10}{BOT_TOKEN[-5:] if BOT_TOKEN else 'N/A'}")
    logger.info(f"API ключ: {'*' * 10}{API_KEY[-5:] if API_KEY else 'N/A'}")
    logger.info("=" * 50)

    try:
        bot.polling(none_stop=True, interval=2, timeout=30)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка бота: {e}")


if __name__ == "__main__":
    main()
