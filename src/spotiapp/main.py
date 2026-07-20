import logging
from utils.logger import setup_logging

logger = logging.getLogger(__file__)


def main():
    print("Hello from spotiapp!")
    setup_logging(level=logging.DEBUG)


if __name__ == "__main__":
    main()
