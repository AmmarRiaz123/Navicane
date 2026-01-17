"""
Run main.py with enhanced debug logging
"""

import logging
import sys

# Set logging to DEBUG level before importing modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run main
from main import main

if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING MAIN.PY WITH DEBUG LOGGING")
    print("=" * 70)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
