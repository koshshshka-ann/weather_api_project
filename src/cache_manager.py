import json
import os
from datetime import datetime, timedelta

# Локальные константы
CACHE_FILE = "weather_cache.json"
CACHE_TTL_HOURS = 3


class CacheManager:
    def __init__(self, cache_file=CACHE_FILE, ttl_hours=CACHE_TTL_HOURS):
        self.cache_file = cache_file
        self.ttl_hours = ttl_hours

    def save(self, city: str, lat: float, lon: float, weather_data: dict) -> None:
        """Сохраняет данные о погоде в кэш."""
        cache_entry = {
            "city": city,
            "lat": lat,
            "lon": lon,
            "weather_data": weather_data,
            "fetched_at": datetime.now().isoformat()
        }

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Не удалось сохранить кэш: {e}")

    def read(self) -> dict | None:
        """Читает данные из кэша, если они не старше TTL."""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            fetched_at = datetime.fromisoformat(cache_data['fetched_at'])
            if datetime.now() - fetched_at > timedelta(hours=self.ttl_hours):
                print("ℹ️ Кэш устарел (больше 3 часов).")
                return None

            return cache_data
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Ошибка чтения кэша: {e}")
            return None
