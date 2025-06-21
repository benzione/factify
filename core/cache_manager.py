import os
import json
import hashlib
import time
from typing import Any, Dict, Optional
from config.settings import CACHE_DIR, CACHE_EXPIRATION_TIME_SECONDS, CACHE_ENABLED
from utils.logger import setup_logging

logger = setup_logging(__name__)

class CacheManager:
    """
    Manages a simple file-based cache for LLM responses.
    Cache keys are generated from the prompt and schema.
    """
    def __init__(self):
        if CACHE_ENABLED:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self._prune_old_cache_files() # Clean up old files on init

    def generate_cache_key(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> str:
        """Generates a unique cache key based on prompt and schema."""
        data_to_hash = prompt
        if schema:
            data_to_hash += json.dumps(schema, sort_keys=True) # Ensure consistent hashing
        return hashlib.md5(data_to_hash.encode('utf-8')).hexdigest()

    def _get_cache_file_path(self, key: str) -> str:
        """Returns the full path for a cache file."""
        return os.path.join(CACHE_DIR, f"{key}.json")

    def set(self, key: str, value: str):
        """
        Stores a value in the cache.
        Includes a timestamp for expiration.
        """
        if not CACHE_ENABLED:
            return

        file_path = self._get_cache_file_path(key)
        cache_entry = {
            "timestamp": time.time(),
            "value": value
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached response for key: {key}")
        except IOError as e:
            logger.error(f"Failed to write to cache file {file_path}: {e}")

    def get(self, key: str) -> Optional[str]:
        """
        Retrieves a value from the cache if it's not expired.
        Returns None if not found or expired.
        """
        if not CACHE_ENABLED:
            return None

        file_path = self._get_cache_file_path(key)
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)

            timestamp = cache_entry.get("timestamp")
            value = cache_entry.get("value")

            if timestamp is None or value is None:
                logger.warning(f"Malformed cache entry for key: {key}. Deleting.")
                os.remove(file_path)
                return None

            if (time.time() - timestamp) > CACHE_EXPIRATION_TIME_SECONDS:
                logger.info(f"Cache entry for key {key} expired. Deleting.")
                os.remove(file_path)
                return None

            logger.debug(f"Retrieved from cache for key: {key}")
            return value
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read or parse cache file {file_path}: {e}. Deleting.")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None

    def _prune_old_cache_files(self):
        """Removes expired cache files from the cache directory."""
        if not CACHE_ENABLED:
            return
        
        logger.info(f"Pruning old cache files in {CACHE_DIR}...")
        current_time = time.time()
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            if not os.path.isfile(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)
                timestamp = cache_entry.get("timestamp")
                
                if timestamp is None or (current_time - timestamp) > CACHE_EXPIRATION_TIME_SECONDS:
                    os.remove(file_path)
                    logger.debug(f"Removed expired cache file: {filename}")
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Could not read or parse cache file {filename} during pruning: {e}. Removing.")
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Unexpected error during cache pruning for {filename}: {e}")

    def clear_cache(self):
        """Clears the entire cache."""
        if not CACHE_ENABLED:
            return
        
        logger.info(f"Clearing cache directory: {CACHE_DIR}")
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting cache file {file_path}: {e}")
        logger.info("Cache cleared.") 