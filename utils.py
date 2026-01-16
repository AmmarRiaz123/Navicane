"""
Utility functions for Smart Cane System
"""

import logging
import time
import os
from functools import wraps
from config import LOG_FILE, LOG_LEVEL

def setup_logger(name):
    """Setup logger with file and console output"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Ensure log directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # File handler
    try:
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        # If file logging fails, just use console
        print(f"Warning: Could not create log file {LOG_FILE}: {e}")
        print("Continuing with console logging only...")
    
    # Console handler (always add this)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    
    return logger

def retry_on_failure(max_attempts=3, delay=1):
    """Decorator to retry function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        continue
                    else:
                        raise e
        return wrapper
    return decorator

class RateLimiter:
    """Rate limiter to prevent repeated actions"""
    def __init__(self, cooldown_seconds):
        self.cooldown = cooldown_seconds
        self.last_triggered = {}
    
    def can_trigger(self, key):
        """Check if enough time has passed since last trigger"""
        now = time.time()
        if key not in self.last_triggered:
            self.last_triggered[key] = now
            return True
        
        if now - self.last_triggered[key] >= self.cooldown:
            self.last_triggered[key] = now
            return True
        
        return False
    
    def reset(self, key):
        """Reset cooldown for a specific key"""
        if key in self.last_triggered:
            del self.last_triggered[key]
