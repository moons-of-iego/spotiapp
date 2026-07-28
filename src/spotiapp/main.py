import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import logging
from src.spotiapp.utils.logger import setup_logging
from src.spotiapp.orchestrator import run

logger = logging.getLogger(__file__)


def main():
    print("Hello from spotiapp!")
    setup_logging(level=logging.INFO)
    run()


if __name__ == "__main__":
    main()
