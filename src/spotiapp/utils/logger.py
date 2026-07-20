import logging
import sys


class CustomFormatter(logging.Formatter):

    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    TIME_FORMAT = "%(asctime)s"

    FORMATS = {
        logging.DEBUG: GREY + "[%(asctime)s] ⚙  [DEBUG] %(message)s" + RESET,
        logging.INFO: RESET + "[%(asctime)s] " + BLUE + "ℹ  %(message)s" + RESET,
        logging.WARNING: YELLOW + "[%(asctime)s] ⚠  [ALERTE] %(message)s" + RESET,
        logging.ERROR: RED + "[%(asctime)s] ✖  [ERREUR] %(message)s" + RESET,
        logging.CRITICAL: RED
        + BOLD
        + "[%(asctime)s] 💥  [CRITIQUE] %(message)s"
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
        logger.addHandler(console_handler)

    return logger
