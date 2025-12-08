"""
Модуль для получения информации о странах
"""
from colorama import init, Fore, Back, Style
from http_client import get

# Инициализируем colorama
init(autoreset=True)


def get_country_info(country_name: str) -> None:
    """
    Получает и выводит информацию о стране

    Args:
        country_name: Название страны на английском
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        data = get(url)

        if not data:
            print(Fore.RED + "Страна не найдена")
            return

        # Берем первую страну из списка
        country = data[0]

        # Извлекаем данные
        name = country.get('name', {})
        common_name = name.get('common', 'Неизвестно')
        official_name = name.get('official', 'Неизвестно')

        capital = ', '.join(country.get('capital', ['Неизвестно']))
        region = country.get('region', 'Неизвестно')

        # Население с форматированием
        population = country.get('population', 0)
        population_formatted = f"{population:,}".replace(',', ' ')

        # Площадь
        area = country.get('area', 0)
        area_formatted = f"{area:,}".replace(',', ' ') if area else "Неизвестно"

        # Валюта
        currencies = country.get('currencies', {})
        if currencies:
            currency_info = []
            for code, info in currencies.items():
                currency_info.append(f"{info.get('name')} ({info.get('symbol', '')})")
            currency_str = ', '.join(currency_info)
        else:
            currency_str = "Неизвестно"

        # Языки
        languages = country.get('languages', {})
        languages_str = ', '.join(languages.values()) if languages else "Неизвестно"

        # Флаг
        flag = country.get('flag', '')

        # Красивый вывод
        print("\n" + "=" * 50)
        print(Fore.CYAN + Back.BLACK + Style.BRIGHT + "ИНФОРМАЦИЯ О СТРАНЕ")
        print("=" * 50)

        print(f"\n{Fore.YELLOW}🏛️  Название:{Style.RESET_ALL}")
        print(f"  Обычное: {Fore.GREEN}{common_name}")
        print(f"  Официальное: {Fore.GREEN}{official_name}")

        print(f"\n{Fore.YELLOW}📍 Основное:{Style.RESET_ALL}")
        print(f"  Столица: {Fore.WHITE}{capital}")
        print(f"  Регион: {Fore.WHITE}{region}")

        print(f"\n{Fore.YELLOW}📊 Статистика:{Style.RESET_ALL}")
        print(f"  Население: {Fore.MAGENTA}{population_formatted} чел.")
        print(f"  Площадь: {Fore.MAGENTA}{area_formatted} км²")

        print(f"\n{Fore.YELLOW}💰 Валюта:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}{currency_str}")

        print(f"\n{Fore.YELLOW}🗣️  Языки:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}{languages_str}")

        print(f"\n{Fore.YELLOW}🎌 Флаг:{Style.RESET_ALL}")
        print(f"  {flag}")

        print("\n" + "=" * 50)

    except Exception as e:
        print(Fore.RED + f"Ошибка при получении информации о стране: {str(e)}")
