"""
Модуль для работы с HTTP-запросами
"""
import requests
from typing import Optional, Dict, Any


class HTTPError(Exception):
    """Кастомное исключение для HTTP-ошибок"""
    pass


def get(url: str, params: Optional[Dict] = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Выполняет GET-запрос к указанному URL

    Args:
        url: Адрес для запроса
        params: Параметры запроса (опционально)
        timeout: Таймаут в секундах

    Returns:
        Словарь с данными ответа (JSON)

    Raises:
        HTTPError: Если статус ответа не 2xx
        ConnectionError: Если проблемы с соединением
        Timeout: Если превышен таймаут
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)

        # Проверяем статус ответа
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            raise HTTPError(
                f"HTTP {response.status_code}: {response.reason}\n"
                f"URL: {url}"
            )

    except requests.exceptions.Timeout:
        raise TimeoutError(f"Таймаут при запросе к {url}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Ошибка соединения с {url}")
    except requests.exceptions.RequestException as e:
        raise HTTPError(f"Ошибка запроса: {str(e)}")
