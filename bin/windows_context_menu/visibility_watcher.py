"""
AEPGP Encrypted File Visibility Watcher

Keeps .enc files hidden when no AEPGP card is present and visible when a card
is attached. Intended to run in the background via Windows startup.
"""

import os
import sys
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
handlers_dir = os.path.join(script_dir, "handlers")
sys.path.insert(0, handlers_dir)

import card_utils
from debug_logger import get_logger

logger = get_logger()

DEFAULT_POLL_INTERVAL_SEC = 5
DEFAULT_RESCAN_INTERVAL_SEC = 60

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "AppData",
}


def get_watch_paths():
    env_paths = os.environ.get("AEPGP_WATCH_PATHS")
    if env_paths:
        paths = [p.strip() for p in env_paths.split(";") if p.strip()]
        return [p for p in paths if os.path.exists(p)]

    user_profile = os.environ.get("USERPROFILE", "")
    if not user_profile:
        return []

    candidates = [
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Downloads"),
    ]
    return [p for p in candidates if os.path.exists(p)]


def iter_encrypted_files(paths):
    for base in paths:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name.lower().endswith(".enc"):
                    yield os.path.join(root, name)


def is_card_present():
    card, error = card_utils.find_aepgp_card()
    try:
        return error is None
    finally:
        if card:
            card.disconnect()


def sync_visibility(paths, card_present):
    hide_files = not card_present
    updated = 0
    failed = 0

    for path in iter_encrypted_files(paths):
        ok, _ = card_utils.set_hidden_attribute(path, hide_files)
        if ok:
            updated += 1
        else:
            failed += 1

    logger.info(
        f"Visibility sync complete. card_present={card_present} "
        f"updated={updated} failed={failed}"
    )


def parse_int_env(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except ValueError:
        return default


def main():
    paths = get_watch_paths()
    if not paths:
        logger.error("No watch paths configured; exiting watcher")
        return 1

    poll_interval = parse_int_env("AEPGP_POLL_INTERVAL_SEC", DEFAULT_POLL_INTERVAL_SEC)
    rescan_interval = parse_int_env("AEPGP_RESCAN_INTERVAL_SEC", DEFAULT_RESCAN_INTERVAL_SEC)

    logger.info(f"Starting visibility watcher. paths={paths}")
    logger.info(
        f"Intervals: poll={poll_interval}s rescan={rescan_interval}s"
    )

    last_state = None
    last_scan = 0

    while True:
        try:
            card_present = is_card_present()
            now = time.time()

            if card_present != last_state or (now - last_scan) >= rescan_interval:
                sync_visibility(paths, card_present)
                last_state = card_present
                last_scan = now

            time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Watcher error: {e}", e)
            time.sleep(poll_interval)


if __name__ == "__main__":
    sys.exit(main())
