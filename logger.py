'''
Filename: logger.py
Description: Logger setup for robot_controller.py
This module sets up a logger that writes logs to a rotating file and also outputs them to the console.

Author: Akshit Gupta
Email: gupta@dwi.rwth-aachen.de
Affiliation: DWI - Leibniz Institute for Interactive Materials

Last Modified: 2025-07-08
Version: 1.0

License:

'''


import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import time

def setup_logger(log_dir = '/home/er/Desktop/Code/logs'):
    os.makedirs(log_dir, exist_ok = True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'asp_{timestamp}.log')
    
    logger = logging.getLogger('ASP')
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes = 1024 * 1024, #1 mb
        backupCount = 1,
        encoding = 'utf-8',
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
    
    
    
