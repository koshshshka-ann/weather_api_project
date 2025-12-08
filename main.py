"""
Главный модуль для работы с API
"""
import sys
import requests
from http_client import get
from country_info import get_country_info
from json_pretty_printer import JsonPrettyPrinter
from colorama import init, Fore, Style, Back
init(autoreset=True)


def show_menu() -> None:
    """Показывает главное меню"""
    print("\n" + "=" * 50)
    print(Fore.CYAN + "🚀 API ПРАКТИКУМ - ГЛАВНОЕ МЕНЮ")
    print("=" * 50)
    print(f"{Fore.GREEN}1{Style.RESET_ALL} - GET запрос по URL")
    print(f"{Fore.GREEN}2{Style.RESET_ALL} - Информация о стране")
    print(f"{Fore.GREEN}3{Style.RESET_ALL} - Случайная собака 🐕")
    print(f"{Fore.RED}0{Style.RESET_ALL} - Выход")
    print("=" * 50)


def make_get_request() -> None:
    """Выполняет GET запрос по введенному URL"""
    try:
        url = input("\nВведите URL для GET запроса: ").strip()

        if not url:
            print(Fore.YELLOW + "URL не может быть пустым!")
            return

        print(Fore.BLUE + "\n⌛ Выполняю запрос...")

        # Засекаем время
        import time
        start_time = time.time()

        # Делаем запрос
        response = requests.get(url)
        response_time = time.time() - start_time

        # Показываем HTTP информацию
        JsonPrettyPrinter.print_http_info(
            url=url,
            method="GET",
            status_code=response.status_code,
            response_time=response_time
        )

        if response.status_code == 200:
            try:
                data = response.json()
                JsonPrettyPrinter.print_json(data, "ОТВЕТ API")

                # Показываем дополнительные подсказки
                print(f"\n{Fore.YELLOW}💡 Советы по работе с данными:{Style.RESET_ALL}")
                if isinstance(data, dict):
                    print(f"  • Используйте data['ключ'] для доступа к значениям")
                elif isinstance(data, list):
                    print(f"  • Используйте data[индекс] или цикл for для перебора")

            except ValueError:
                # Если не JSON, показываем текст
                print(f"{Fore.YELLOW}📄 Текстовый ответ (не JSON):{Style.RESET_ALL}")
                print("-" * 40)
                print(response.text[:1000])
                if len(response.text) > 1000:
                    print(f"\n{Fore.YELLOW}... и еще {len(response.text) - 1000} символов")
        else:
            print(f"{Fore.RED}❌ Ошибка HTTP {response.status_code}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Ответ сервера:{Style.RESET_ALL}")
            print(response.text[:500])

    except Exception as e:
        print(Fore.RED + f"\n❌ Ошибка: {str(e)}")


def get_random_dog() -> None:
    """Получает ссылку на случайное изображение собаки"""
    try:
        print(Fore.BLUE + "\n🐶 Ищу случайную собачку...")

        url = "https://dog.ceo/api/breeds/image/random"
        data = get(url)

        if data.get('status') == 'success':
            image_url = data.get('message', '')

            print(Fore.GREEN + "\n✅ Нашел собаку!")
            print(Fore.YELLOW + "\n📷 Ссылка на изображение:")
            print(Fore.CYAN + image_url)

            # Парсим породу из URL
            if '/breeds/' in image_url:
                breed = image_url.split('/breeds/')[1].split('/')[0]
                print(f"\n🏷️  Порода: {Fore.WHITE}{breed.replace('-', ' ').title()}")

        else:
            print(Fore.RED + "Не удалось получить изображение собаки")

    except Exception as e:
        print(Fore.RED + f"\n❌ Ошибка: {str(e)}")


def get_country_from_user() -> None:
    """Запрашивает у пользователя название страны"""
    country = input("\nВведите название страны (на английском): ").strip()

    if not country:
        print(Fore.YELLOW + "Название страны не может быть пустым!")
        return

    get_country_info(country)


def demo_different_apis() -> None:
    """Демонстрация работы с разными API"""
    print(f"\n{Fore.CYAN}🚀 ДЕМО РАЗНЫХ API{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Выберите API для демонстрации:{Style.RESET_ALL}")

    apis = {
        "1": ("Случайная собака", "https://dog.ceo/api/breeds/image/random"),
        "2": ("Информация о стране", "https://restcountries.com/v3.1/name/france"),
        "3": ("Фейковые товары", "https://fakestoreapi.com/products/1"),
        "4": ("Шутка про Чак Норриса", "https://api.chucknorris.io/jokes/random"),
        "5": ("Котики", "https://api.thecatapi.com/v1/images/search"),
        "6": ("Своя ссылка", None)
    }

    for key, (name, url) in apis.items():
        print(f"  {Fore.GREEN}{key}{Style.RESET_ALL} - {name}")

    choice = input(f"\n{Fore.CYAN}Выберите (1-6): {Style.RESET_ALL}").strip()

    if choice == "6":
        url = input("Введите свой URL: ").strip()
        if not url:
            print(Fore.RED + "URL не может быть пустым!")
            return
    elif choice in apis:
        url = apis[choice][1]
    else:
        print(Fore.RED + "Неверный выбор!")
        return

    # Выполняем запрос
    make_get_request_url(url)


def make_get_request_url(url: str) -> None:
    """Выполняет GET запрос по указанному URL"""
    try:
        print(Fore.BLUE + f"\n⌛ Запрашиваю {url}...")

        import time
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response_time = time.time() - start_time

        JsonPrettyPrinter.print_http_info(
            url=url,
            method="GET",
            status_code=response.status_code,
            response_time=response_time
        )

        if response.status_code == 200:
            try:
                data = response.json()
                JsonPrettyPrinter.print_json(data, "ОТВЕТ API")
            except ValueError:
                print(f"{Fore.YELLOW}📄 Текстовый ответ:{Style.RESET_ALL}")
                print("-" * 40)
                print(response.text[:500])
        else:
            print(f"{Fore.RED}❌ Ошибка {response.status_code}{Style.RESET_ALL}")

    except Exception as e:
        print(Fore.RED + f"❌ Ошибка: {str(e)}")


def main() -> None:
    """Главная функция программы"""
    # Импорты здесь, чтобы не было circular imports
    from colorama import init, Fore, Style
    init(autoreset=True)

    print(Fore.MAGENTA + "\n🌟 Добро пожаловать в API Практикум!")
    print(Fore.YELLOW + "Выполняем домашнее задание по работе с API")

    while True:
        print("\n" + "=" * 50)
        print(Fore.CYAN + "🚀 УНИВЕРСАЛЬНЫЙ API КЛИЕНТ")
        print("=" * 50)
        print(f"{Fore.GREEN}1{Style.RESET_ALL} - GET запрос по URL")
        print(f"{Fore.GREEN}2{Style.RESET_ALL} - Информация о стране")
        print(f"{Fore.GREEN}3{Style.RESET_ALL} - Случайная собака")
        print(f"{Fore.GREEN}4{Style.RESET_ALL} - Демо разных API")
        print(f"{Fore.GREEN}5{Style.RESET_ALL} - JSON Pretty Printer (тест)")
        print(f"{Fore.RED}0{Style.RESET_ALL} - Выход")
        print("=" * 50)

        choice = input(f"\n{Fore.YELLOW}Выберите пункт: {Style.RESET_ALL}").strip()

        if choice == "0":
            print(Fore.MAGENTA + "\n👋 До свидания!")
            break
        elif choice == "1":
            make_get_request()
        elif choice == "2":
            get_country_from_user()
        elif choice == "3":
            get_random_dog()
        elif choice == "4":
            demo_different_apis()
        elif choice == "5":
            # Тест pretty printer
            from json_pretty_printer import JsonPrettyPrinter
            test_data = {
                "message": "Привет! Это тестовые данные.",
                "number": 42,
                "is_cool": True,
                "list": [1, 2, 3, "четыре"],
                "nested": {"key": "value", "null": None}
            }
            JsonPrettyPrinter.print_json(test_data, "ТЕСТ ПРИНТЕРА")
        else:
            print(Fore.RED + "❌ Неверный выбор!")


if __name__ == "__main__":
    main()
