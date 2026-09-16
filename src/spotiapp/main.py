import os
import certifi
import argparse

os.environ["SSL_CERT_FILE"] = certifi.where()

import logging
from spotiapp.utils.logger import setup_logging
from spotiapp.orchestrator import run
from spotiapp.db.database_manager import DatabaseManager

logger = logging.getLogger(__file__)


def main():
    setup_logging(level=logging.INFO)
    logger.info("===== SPOTIAPP =====")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- sub-command : run ---
    parser_run = subparsers.add_parser("run", help="Update database content.")
    parser_run.add_argument(
        "--force-reload",
        action="store_true",
        dest="force_reload",
        help="Force the reload of the database. May take time.",
    )

    # --- sub-command : update-db ---
    parser_update = subparsers.add_parser(
        "update-db", help="Update the database scheme."
    )
    parser_update.add_argument(
        "sql_script",
        type=str,
        help="The relative filepath to the .sql update script file.",
    )

    args = parser.parse_args()

    if args.command == "run":
        run(force_reload=args.force_reload)
    elif args.command == "update-db":
        DatabaseManager.update_database_scheme(args.sql_script)


if __name__ == "__main__":
    main()
