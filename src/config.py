import os
import logging
from dotenv import load_dotenv

"""
src/config.py
-------------
Purpose: Centralizes environment configuration and logging setup.
It reads variables from the `.env` file to securely toggle debug modes 
without requiring changes to the core code structure natively.
"""

load_dotenv()

def get_logger(name):
    """Returns a configured logger based on .env logic."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure root logging if not already configured
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(name)
