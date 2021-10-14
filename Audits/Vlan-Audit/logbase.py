# This module can be imported in any python script to start logging immedietly
# example to start a logger: logger_debug = setup_logger('debugger', 'logs/{}/debug.log'.format(date.today()))
# Simply this will call the setup_logger function and create a new logger "debugger" if doesn't exist.
# to call the logger anywhere in your code:     logger_debug = logging.getLogger("debugger")


import logging, os

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # Checking if the folder exists or not
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def setup_logger_override(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # Checking if the folder exists or not
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    handler = logging.FileHandler(log_file, 'w+')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

