import logging
import sys
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    # Remove default handlers
    logging.root.handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]

    # Configure Loguru
    from app.services.log_streamer import log_streamer
    
    def log_streamer_sink(message):
        record = message.record
        time_str = record["time"].strftime("%H:%M:%S")
        level_str = record["level"].name
        msg_str = record["message"]
        log_streamer.push_log(f"{time_str} | {level_str} | {msg_str}")

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            },
            {
                "sink": log_streamer_sink,
                "format": "{time:HH:mm:ss} | {level} | {message}",
            }
        ]
    )

    return logger
