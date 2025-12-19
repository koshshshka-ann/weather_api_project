import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict


class CacheManager:
    def __init__(self, cache_file: str = "weather_cache.json", ttl_hours: int = 3):
        self.cache_file = cache_file
        self.ttl_hours = ttl_hours

    def save_weather(self, city: str, lat: float, lon: float, weather_data: Dict) -> None:
        cache_entry = {
            "city": city,
            "lat": lat,
            "lon": lon,
            "weather_data": weather_data,
            "fetched_at": datetime.now().isoformat(),
            "type": "weather"
        }
        self._save_cache(cache_entry)

    def save_forecast(self, lat: float, lon: float, forecast_data: Dict) -> None:
        cache_entry = {
            "lat": lat,
            "lon": lon,
            "forecast_data": forecast_data,
            "fetched_at": datetime.now().isoformat(),
            "type": "forecast"
        }
        self._save_cache(cache_entry)

    def read_weather(self) -> Optional[Dict]:
        cache_data = self._read_cache()
        if cache_data and cache_data.get("type") == "weather":
            return cache_data
        return None

    def read_forecast(self) -> Optional[Dict]:
        cache_data = self._read_cache()
        if cache_data and cache_data.get("type") == "forecast":
            return cache_data
        return None

    def _save_cache(self, cache_entry: Dict) -> None:
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Не удалось сохранить кэш: {e}")

    def _read_cache(self) -> Optional[Dict]:
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            fetched_at = datetime.fromisoformat(cache_data['fetched_at'])
            if datetime.now() - fetched_at > timedelta(hours=self.ttl_hours):
                return None

            return cache_data
        except (IOError, json.JSONDecodeError, KeyError):
            return None
