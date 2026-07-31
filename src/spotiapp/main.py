import os
import certifi
import argparse

os.environ["SSL_CERT_FILE"] = certifi.where()

import logging
from spotiapp.utils.logger import setup_logging
from spotiapp.orchestrator import run

logger = logging.getLogger(__file__)


def main():
    setup_logging(level=logging.INFO)
    logger.info("===== SPOTIAPP =====")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-reload",
        action="store_true",
        dest="force_reload",
        help="Force the reload of the database. May take time.",
    )
    args = parser.parse_args()
    run(force_reload=args.force_reload)


if __name__ == "__main__":
    main()
