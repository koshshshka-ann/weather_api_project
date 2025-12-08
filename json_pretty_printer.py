"""
Универсальный красивизатор JSON для любых API ответов
"""
from colorama import init, Fore, Back, Style
import json
from typing import Any, Dict, List
import textwrap

init(autoreset=True)


class JsonPrettyPrinter:
    """Красиво форматирует любой JSON с цветами и стилем"""

    # Цветовые схемы для разных типов данных
    COLORS = {
        'key': Fore.CYAN,
        'string': Fore.GREEN,
        'number': Fore.YELLOW,
        'boolean': Fore.MAGENTA,
        'null': Fore.RED,
        'bracket': Fore.WHITE,
        'header': Fore.CYAN + Style.BRIGHT,
        'type': Fore.BLUE,
    }

    @staticmethod
    def print_json(data: Any, title: str = "ДАННЫЕ API") -> None:
        """
        Красиво печатает любой JSON

        Args:
            data: Данные для вывода (dict, list или строка JSON)
            title: Заголовок для вывода
        """
        try:
            # Если пришла строка - парсим
            if isinstance(data, str):
                data = json.loads(data)

            print(f"\n{JsonPrettyPrinter.COLORS['header']}{'═' * 60}")
            print(f"📊 {title}")
            print(f"{'═' * 60}{Style.RESET_ALL}\n")

            JsonPrettyPrinter._print_value(data, "", is_root=True)

            print(f"\n{JsonPrettyPrinter.COLORS['header']}{'═' * 60}")
            print(f"🎯 Сводка: {JsonPrettyPrinter._get_summary(data)}")
            print(f"{'═' * 60}{Style.RESET_ALL}")

        except (json.JSONDecodeError, TypeError) as e:
            print(f"{Fore.RED}❌ Ошибка форматирования JSON: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}📦 Сырые данные:{Style.RESET_ALL}")
            print(str(data)[:500] + ("..." if len(str(data)) > 500 else ""))

    @staticmethod
    def _print_value(value: Any, indent: str, is_root: bool = False, is_last: bool = True) -> None:
        """Рекурсивно печатает значение с правильным форматированием"""

        # Определяем тип значения
        value_type = type(value).__name__
        type_indicator = f"{Fore.BLUE}[{value_type}]{Style.RESET_ALL} "

        if isinstance(value, dict):
            print(f"{indent}{JsonPrettyPrinter.COLORS['bracket']}{{{Style.RESET_ALL}")

            items = list(value.items())
            for i, (key, val) in enumerate(items):
                # Ключ
                key_str = f"{JsonPrettyPrinter.COLORS['key']}{json.dumps(key)}{Style.RESET_ALL}: "

                # Значение
                new_indent = indent + "  "
                is_last_item = (i == len(items) - 1)

                # Для простых значений выводим в одну строку
                if isinstance(val, (str, int, float, bool)) or val is None:
                    value_str = JsonPrettyPrinter._format_simple_value(val)
                    print(f"{new_indent}{key_str}{value_str}", end="")

                    # Показываем тип для простых значений
                    if not isinstance(val, str) or len(str(val)) < 30:
                        print(f" {Fore.BLUE}[{type(val).__name__}]{Style.RESET_ALL}", end="")

                    if not is_last_item:
                        print(",")
                    else:
                        print()
                else:
                    # Для сложных значений - рекурсивно
                    print(f"{new_indent}{key_str}")
                    JsonPrettyPrinter._print_value(val, new_indent + "  ", is_last=is_last_item)

                    if not is_last_item:
                        print(f"{new_indent}{JsonPrettyPrinter.COLORS['bracket']},{Style.RESET_ALL}")

            bracket = "}" if is_last else "},"
            print(f"{indent}{JsonPrettyPrinter.COLORS['bracket']}{bracket}{Style.RESET_ALL}")

        elif isinstance(value, list):
            print(f"{indent}{JsonPrettyPrinter.COLORS['bracket']}[{Style.RESET_ALL}")

            for i, item in enumerate(value[:10]):  # Показываем первые 10 элементов
                new_indent = indent + "  "
                is_last_item = (i == len(value[:10]) - 1) or (i == 9)

                # Для списков показываем индекс
                index_str = f"{Fore.WHITE}[{i}]{Style.RESET_ALL} "

                if isinstance(item, (dict, list)):
                    print(f"{new_indent}{index_str}")
                    JsonPrettyPrinter._print_value(item, new_indent + "  ", is_last=is_last_item)
                else:
                    value_str = JsonPrettyPrinter._format_simple_value(item)
                    print(f"{new_indent}{index_str}{value_str}", end="")

                    if not is_last_item:
                        print(",")
                    else:
                        print()

                if i == 9 and len(value) > 10:
                    print(f"{new_indent}{Fore.YELLOW}... и еще {len(value) - 10} элементов{Style.RESET_ALL}")
                    break

            bracket = "]" if is_last else "],"
            print(f"{indent}{JsonPrettyPrinter.COLORS['bracket']}{bracket}{Style.RESET_ALL}")

        else:
            # Простые значения
            value_str = JsonPrettyPrinter._format_simple_value(value)
            print(f"{indent}{value_str}", end="")

    @staticmethod
    def _format_simple_value(value: Any) -> str:
        """Форматирует простое значение с цветом"""
        if isinstance(value, str):
            # Обрезаем длинные строки
            if len(value) > 50:
                value = value[:47] + "..."
            return f"{JsonPrettyPrinter.COLORS['string']}{json.dumps(value)}{Style.RESET_ALL}"

        elif isinstance(value, (int, float)):
            return f"{JsonPrettyPrinter.COLORS['number']}{value}{Style.RESET_ALL}"

        elif isinstance(value, bool):
            bool_str = "true" if value else "false"
            return f"{JsonPrettyPrinter.COLORS['boolean']}{bool_str}{Style.RESET_ALL}"

        elif value is None:
            return f"{JsonPrettyPrinter.COLORS['null']}null{Style.RESET_ALL}"

        else:
            return f"{Fore.RED}???{Style.RESET_ALL}"

    @staticmethod
    def _get_summary(data: Any) -> str:
        """Возвращает краткую сводку о данных"""
        if isinstance(data, dict):
            keys = list(data.keys())
            if len(keys) > 5:
                keys_preview = ", ".join(keys[:3]) + f" ... ({len(keys)} ключей)"
            else:
                keys_preview = ", ".join(keys)
            return f"Объект с ключами: {keys_preview}"

        elif isinstance(data, list):
            if len(data) == 0:
                return "Пустой список"
            elif len(data) == 1:
                return f"Список из 1 элемента"
            else:
                first_type = type(data[0]).__name__ if data else "unknown"
                return f"Список из {len(data)} элементов (тип первого: {first_type})"

        else:
            return f"Простое значение: {type(data).__name__}"

    @staticmethod
    def print_http_info(url: str, method: str, status_code: int, response_time: float = None) -> None:
        """Красиво выводит информацию о HTTP запросе"""
        print(f"\n{Back.BLUE}{Fore.WHITE}{' ' * 60}")
        print(f"{' ' * 15}🌐 HTTP ЗАПРОС {' ' * 15}")
        print(f"{' ' * 60}{Style.RESET_ALL}\n")

        # Статус код с цветом
        if 200 <= status_code < 300:
            status_color = Fore.GREEN
            status_emoji = "✅"
        elif 300 <= status_code < 400:
            status_color = Fore.YELLOW
            status_emoji = "↪️"
        elif 400 <= status_code < 500:
            status_color = Fore.RED
            status_emoji = "❌"
        elif 500 <= status_code < 600:
            status_color = Fore.MAGENTA
            status_emoji = "🔥"
        else:
            status_color = Fore.WHITE
            status_emoji = "❓"

        info = [
            f"{Fore.CYAN}📡 Метод:{Style.RESET_ALL} {Fore.WHITE}{method.upper()}{Style.RESET_ALL}",
            f"{Fore.CYAN}🌐 URL:{Style.RESET_ALL} {Fore.WHITE}{url}{Style.RESET_ALL}",
            f"{Fore.CYAN}📊 Статус:{Style.RESET_ALL} {status_color}{status_emoji} {status_code}{Style.RESET_ALL}",
        ]

        if response_time is not None:
            info.append(f"{Fore.CYAN}⏱️ Время:{Style.RESET_ALL} {Fore.WHITE}{response_time:.2f} сек{Style.RESET_ALL}")

        print("\n".join(info))
        print()


# Пример использования
if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        "user": {
            "id": 12345,
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": True,
            "roles": ["admin", "user"],
            "metadata": {
                "created_at": "2023-01-15",
                "last_login": None,
                "login_count": 42
            }
        },
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Mouse", "price": 19.99},
            {"id": 3, "name": "Keyboard", "price": 49.99}
        ],
        "settings": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    }

    # Демонстрация
    JsonPrettyPrinter.print_json(test_data, "ТЕСТОВЫЕ ДАННЫЕ")

    # Демонстрация HTTP информации
    JsonPrettyPrinter.print_http_info(
        url="https://api.example.com/users",
        method="GET",
        status_code=200,
        response_time=0.45
    )
