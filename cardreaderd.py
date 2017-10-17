#!/usr/bin/env python3
import os, re, logging
import urllib.request as request
from urllib.error import HTTPError
from subprocess import Popen, PIPE

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)

authorized_cards_url = os.getenv("AUTHORIZED_CARDS_URL", "")
reader_daemon = "./barbatos/barbatos"

testing = os.getenv("TESTING", False)
if testing:
  reader_daemon = "./test/reader-daemon"
  authorized_cards_url = "file:///" + os.getcwd() + "/test/card_ids.txt"

card_id_pattern = re.compile("(0x[a-f0-9]+)", re.IGNORECASE)
authorized_cards = []

def reload_cards():
  try:
    with request.urlopen(authorized_cards_url) as req:
      log.info("Got some new card data")
      lines = req.read().decode('utf-8').split("\n")
      if len(lines) < 1:
        log.error("Got less than 1 line of data. Keeping old list.")
        return

      old_len = len(authorized_cards)
      authorized_cards.clear()
      authorized_cards.extend(lines)
      log.info("Reloaded authorized cards list (before: %d, now: %d)" % (old_len, len(authorized_cards)))
  except HTTPError as e:
    log.error("Request returned error: %s" % e)
    log.info("Using existing list. No updates made.")
  except ValueError:
    log.error("Invalid URL for authorized cards")

def auth_card(card_id):
  return authorized_cards.count(card_id) > 0

def open_door():
  with Popen(["./open-door"]) as proc:
    try:
      proc.wait(timeout=10)
    except TimeoutExpired:
      log.error('Timeout exceeded while waiting for door to open')
    return proc.returncode == 0

if __name__ == "__main__":
  reload_cards()
  log.debug(authorized_cards)
  with Popen([reader_daemon], stdout=PIPE) as proc:
    for line in iter(proc.stdout.readline, b""):
      search = re.search(card_id_pattern, line.decode("utf-8"))
      if search is None:
        log.debug("No card id matched in: %s" % line.decode("utf-8"))
        continue

      card_id = search.group(1)
      if not auth_card(card_id):
        log.error("Unauthorized card %s" % card_id)
        continue

      log.info("Card %s is authorized" % card_id)
      if open_door():
        log.info("Door opened")
      else:
        log.error("Failed to open door")

