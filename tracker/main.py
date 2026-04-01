"""
Точка входа Budget VR Tracker.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import Config

log = logging.getLogger(__name__)


async def main_async(config: Config):
    log.info("Запуск Budget VR Tracker...")
    log.info("Конфигурация: webcam=%d, phone=%s", 
             config.cameras.webcam_index,
             "enabled" if config.cameras.phone_enabled else "disabled")
    
    # TODO: Implement full pipeline
    log.info("Pipeline в разработке...")


def main():
    parser = argparse.ArgumentParser(description="Budget VR Tracker")
    parser.add_argument("--phone-ip", help="Phone IP for IP Webcam")
    parser.add_argument("--no-phone", action="store_true", help="Disable phone camera")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    config = Config()
    
    if args.no_phone or not args.phone_ip:
        config.cameras.phone_enabled = False
    elif args.phone_ip:
        config.cameras.phone_url = f"http://{args.phone_ip}:8080/video"

    try:
        asyncio.run(main_async(config))
    except KeyboardInterrupt:
        log.info("Stopped by user")


if __name__ == "__main__":
    main()
