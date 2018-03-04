import json
import sys
import time
import subprocess
import re
import os
import threading
from syslogger import Syslogger
from base64 import b64encode
from urllib.request import Request, urlopen

CARD_PATTERN = re.compile("(0x[a-f0-9]+)", re.IGNORECASE)
CARD_READER_BIN = os.getenv("CARD_READER_BIN", default="./nfcreader/nfcreader")
OPEN_DOOR_BIN = os.getenv("OPEN_DOOR_BIN", default="./open-door")

CARD_DATA_URL = os.getenv("CARD_DATA_URL")
CARD_DATA_USERNAME = os.getenv("CARD_DATA_USERNAME")
CARD_DATA_PASSWORD = os.getenv("CARD_DATA_PASSWORD")

UPDATE_INTERVAL = 15
CARDS_SAVE_FILE = os.getenv("CARD_DATA_FILE", default="./.card_data")

# TODO: Make this into something nice with logging library
#DEBUG = bool(os.getenv("DEBUG", False))
TESTING = bool(os.getenv("TESTING", False))
if TESTING:
    CARD_READER_BIN = "./test/nfcreader-mock"
    OPEN_DOOR_BIN = ["echo", "Door opened!"]
    CARDS_SAVE_FILE = "/tmp/testfile"

logger = Syslogger()

class DoorControl:
    def __init__(self):
        # Master list of authorized cards, shared between threads
        self.authorized_cards = list()

    def run(self):
        # Attempt to start off from last successful download
        self.load_saved_cards()

        # Start NFC card reader thread, that also opens the door
        logger.info("Starting NFC card reader thread")
        nfc_thread = threading.Thread(target=DoorControl.nfc_reader_worker, args=(self,))
        nfc_thread.start()

        logger.info("Updating list of authorized cards every %d second(s)", UPDATE_INTERVAL)

        last_download_failed = True

        while nfc_thread.is_alive():
            # Download new cards and update list if necessary
            try:
                fresh_cards = self.download_card_data()

                if last_download_failed:
                    logger.info("Successfully downloaded card data")
                    last_download_failed = False

                if len(fresh_cards) > 0 and fresh_cards != self.authorized_cards:
                    logger.info("Now there are %d authorized card(s) (was %d)", len(fresh_cards), len(self.authorized_cards))
                    self.authorized_cards = fresh_cards
                    # Persist successfully downloaded lists
                    self.save_cards()
            except Exception as e:
                last_download_failed = True
                logger.error("Failed to download new card data: %s", e)

            time.sleep(UPDATE_INTERVAL)

        logger.warning("Card reader thread stopped. Exiting!")


    def load_saved_cards(self):
        try:
            with open(CARDS_SAVE_FILE, "r") as f:
                deserialized = f.read().strip().split(',')
                if type(deserialized) is list:
                    self.authorized_cards = deserialized
                    logger.info("Successfully loaded last used list of cards (%d cards)", len(self.authorized_cards))
                else:
                    logger.error("File with authorized cards was invalid format. Starting from scratch.")
        except FileNotFoundError:
            logger.info("File with authorized cards not found. Starting from scratch.")


    def save_cards(self):
        try:
            serialized = ','.join(self.authorized_cards)
            with open(CARDS_SAVE_FILE, "w") as f:
                f.write(serialized)
            logger.info("Saved list of authorized cards to file", CARDS_SAVE_FILE)
        except Exception as e:
            # TODO: Catch a less generic exception. Just not quite sure if it's necessary to be very defensive here
            logger.error("An error occured while attempting to save list of cards: %s", e)


    def download_card_data(self):
        # Build an authenticated request
        req = Request(CARD_DATA_URL)
        credentials = CARD_DATA_USERNAME + ":" + CARD_DATA_PASSWORD
        auth_str = b64encode(credentials.encode()).decode("ascii")
        req.add_header("Authorization", "Basic " + auth_str)

        cards = list()

        with urlopen(req) as res:
            user_data = json.loads(res.read().decode())

            # Expect an array
            if type(user_data) is not list:
                raise ValueError("Invalid data format %s. Expected %s", type(user_data), list)

            # Extract card numbers from all users that have a registered card
            k = "card_number"
            for user in user_data:
                if k in user and len(user[k]) > 0:
                    cards.append(user[k])

        return cards


    def nfc_reader_worker(self):
        with subprocess.Popen(CARD_READER_BIN, bufsize=1, stdout=subprocess.PIPE) as proc:
            # TODO: When Python 3.6 is supported on target system, use `encoding` kwarg with Popen
            # TODO: Pretty sure there's a more pythonic way
            for line in iter(proc.stdout.readline, b''):
                line = line.decode("utf-8")

                # Match on successful NFC tag reads
                card_match = CARD_PATTERN.search(line[:-1])
                if card_match is None:
                    logger.debug("card_id regex pattern did not match: '%s'", line[:-1])
                    continue

                # Verify card is authorized
                card_id = card_match.group(1)
                if card_id not in self.authorized_cards:
                    logger.warning("Card NOT authorized: %s", card_id)
                    continue

                logger.info("Card authorized: %s", card_id)

                # Trigger door lock
                try:
                    with subprocess.Popen(OPEN_DOOR_BIN) as proc:
                        proc.wait(timeout=10)
                        if proc.returncode == 0:
                            logger.info("Door lock trigger script exited successfully")
                        else:
                            logger.error("Door lock trigger script exited uncleanly: %d)", proc.returncode)
                            (stdout, stderr) = proc.communicate()
                            logger.debug(stderr)
                except subprocess.TimeoutExpired:
                    logger.error("Timed out waiting for lock trigger script to exit")


if __name__ == '__main__':
    DoorControl().run()
