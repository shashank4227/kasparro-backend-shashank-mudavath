import logging
from pythonjsonlogger import jsonlogger

def configure_logging():
    """
    Configures the root logger to output logs in structured JSON format.
    """
    logger = logging.getLogger()
    
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplication/conflict
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
