import argparse
import asyncio
import logging
import sys

from dummy_bot.config.config import get_config
from dummy_bot.internal.app.app import App


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='Path to .env file')
    args = parser.parse_args()

    cfg = get_config(args.env)

    app = App(cfg)

    asyncio.run(app.run())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    main()
