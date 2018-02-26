import json
import sys
import time
import subprocess
import io
import re
import threading
from base64 import b64encode
from urllib.request import Request, urlopen

CARD_DATA_URL = "https://hackeriet.no/hula/member/all_members.json"
CARD_PATTERN = re.compile("(0x[a-f0-9]+)", re.IGNORECASE)
CARD_READER_BIN = ["./test/nfcreader-mock"]
OPEN_DOOR_BIN = ["echo", "Door opened!"]
USERNAME = ""
PASSWORD = ""
UPDATE_INTERVAL = 15
CARDS_SAVE_FILE = "/tmp/testfile"

class DoorControl:
    def run(self):
        # Master list of authorized cards, shared between threads
        self.authorized_cards = list()

        # Attempt to start off from last successful download
        self.load_saved_cards()

        # Start NFC card reader thread, that also opens the door
        print("Starting NFC card reader thread")
        nfc_thread = threading.Thread(target=DoorControl.nfc_reader_worker, args=(self,))
        nfc_thread.start()

        print("Updating list of authorized cards every %d second(s)" % UPDATE_INTERVAL)

        while nfc_thread.is_alive():
            # Download new cards and update list if necessary
            try:
                fresh_cards = self.download_card_data()
                if len(fresh_cards) > 0 and fresh_cards != self.authorized_cards:
                    print("Now %d authorized card(s) (was %d)" % (len(fresh_cards), len(self.authorized_cards)))
                    self.authorized_cards = fresh_cards
                    # Persist successfully downloaded lists
                    self.save_cards()
            except Exception as e:
                print("Failed to download new card data", e, file=sys.stderr)

            time.sleep(UPDATE_INTERVAL)

        print("Card reader thread stopped. Exiting!")

    def load_saved_cards(self):
        try:
            with open(CARDS_SAVE_FILE, "r") as f:
                deserialized = f.read().strip().split(',')
                if type(deserialized) is list:
                    self.authorized_cards = deserialized
                    print("Successfully loaded last used list of cards (%d cards)" % len(self.authorized_cards))
                else:
                    print("File with authorized cards was invalid format. Starting from scratch.", file=sys.stderr)
        except FileNotFoundError:
            print("File with authorized cards not found. Starting from scratch.")


    def save_cards(self):
        try:
            serialized = ','.join(self.authorized_cards)
            with open(CARDS_SAVE_FILE, "w") as f:
                f.write(serialized)
            print("Saved list of authorized cards to file", CARDS_SAVE_FILE)
        except Exception as e:
            # TODO: Catch a less generic exception. Just not quite sure if it's necessary to be very defensive here
            print("An error occured while attempting to save list of cards", e, file=sys.stderr)


    def download_card_data(self):
        # Build an authenticated request
        req = Request(CARD_DATA_URL)
        credentials = USERNAME + ":" + PASSWORD
        auth_str = b64encode(credentials.encode()).decode("ascii")
        req.add_header("Authorization", "Basic " + auth_str)

        cards = list()

        with urlopen(req) as res:
            user_data = json.loads(res.read().decode())

            # Expect an array
            if type(user_data) is not list:
                raise ValueError("Invalid data format %s. Expected %s" % (type(user_data), list))

            # Extract card numbers from all users that have a registered card
            k = "card_number"
            for user in user_data:
                if k in user and len(user[k]) > 0:
                    cards.append(user[k])

        return cards


    def nfc_reader_worker(self):
        with subprocess.Popen(CARD_READER_BIN, encoding="utf-8", bufsize=1, stdout=subprocess.PIPE) as proc:
            for line in iter(proc.stdout.readline, ''):
                # Match on successful NFC tag reads
                card_match = CARD_PATTERN.search(line[:-1])
                if card_match is None:
                    continue

                # Verify card is authorized
                card_id = card_match.group(1)
                if card_id not in self.authorized_cards:
                    print("Card %s was rejected access: Not authorized" % card_id)
                    continue

                # Trigger door lock
                try:
                    with subprocess.Popen(OPEN_DOOR_BIN) as proc:
                        proc.wait(timeout=10)
                        if proc.returncode == 0:
                            print("Door lock trigger script exited successfully")
                        else:
                            print("Door lock trigger script exited uncleanly: %d)" % (proc.returncode), file=sys.stderr)
                except subprocess.TimeoutExpired:
                    print("Timed out waiting for lock trigger script to exit", file=sys.stderr)


if __name__ == '__main__':
    DoorControl().run()

