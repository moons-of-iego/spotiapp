import logging
import sys


class BlockNoisyFilesFilter(logging.Filter):
    def filter(self, record):
        if record.filename == "_client.py":
            return False
        return True


class CustomFormatter(logging.Formatter):
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    FORMATS = {
        logging.DEBUG: GREY
        + "%(filename)-15s [%(asctime)s] ⚙  [DEBUG] %(message)s"
        + RESET,
        logging.INFO: RESET
        + "%(filename)-15s [%(asctime)s] "
        + BLUE
        + "ℹ  %(message)s"
        + RESET,
        logging.WARNING: YELLOW
        + "%(filename)-15s [%(asctime)s] ⚠  [ALERTE] %(message)s"
        + RESET,
        logging.ERROR: RED
        + "%(filename)-15s [%(asctime)s] ✖  [ERREUR] %(message)s"
        + RESET,
        logging.CRITICAL: RED
        + BOLD
        + "%(filename)-15s [%(asctime)s] 💥  [CRITIQUE] %(message)s"
        + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, "%(message)s")
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logging(level=logging.INFO):
    """Configure le système de logs pour l'application."""
    logger = logging.getLogger()
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())

        console_handler.addFilter(BlockNoisyFilesFilter())

        logger.addHandler(console_handler)

    # Shut down logs on some librairies
    logging.getLogger("pylast").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger
