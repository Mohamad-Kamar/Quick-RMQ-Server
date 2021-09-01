import logging
import logging.handlers
import os
import sys
import time

MSG_FORMAT = '[%(asctime)s.%(msecs)03dZ] [%(levelname)s] [%(app_name)s] [%(app_code)s] [TINAA_BSAF] [%(module)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

log_conf = {
    'location': '../logs/',
    'level': 'INFO',
    'log_file_name': 'l3vpn-controller',
    'app_code': '0017',
    'app_name': 'l3vpn-controller'
}

class HomaLoggerAdapter(logging.LoggerAdapter):
    pass

def get_homa_logger(name):
    """
    function to customize logger based on APP specific settings

    Parameters
    ----------
    name: str
        name of the logger
    """
    # get logger
    logger = logging.getLogger(name)
    logger.setLevel(log_conf['level'])
    # Define the location of the log file, if no directory then create new directory
    location = log_conf['location']
    if not os.path.exists(location):
        os.makedirs(location)
    file_name = "{}.log".format(log_conf['log_file_name'])
    file_location = location + file_name
    # Define the formatter
    fmtr = logging.Formatter(fmt=MSG_FORMAT, datefmt=DATE_FORMAT)
    fmtr.converter = time.gmtime
    # Define file handlers and attach them to the logger
    if not len(logger.handlers):
        file_handler = logging.handlers.TimedRotatingFileHandler(file_location, when='midnight', interval=1, backupCount=7, utc=True)
        file_handler.setFormatter(fmtr)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(fmtr)
        # logger.addHandler(file_handler)
        logger.addHandler(stderr_handler)
    format_conf = {'app_code': log_conf['app_code'], 'app_name': log_conf['app_name']}
    logger = HomaLoggerAdapter(logger, format_conf)
    return logger


logger = get_homa_logger('l3vpn-orchestrator')