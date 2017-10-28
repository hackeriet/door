#!/usr/bin/env python3
import os, re, json, sys, traceback
from urllib.request import Request, urlparse, urlopen
from urllib.error import HTTPError
from subprocess import Popen, PIPE
from base64 import b64encode
import syslogger

log = syslogger.getLogger()

authorized_cards_url = os.getenv("AUTHORIZED_CARDS_URL", "")
reader_daemon = os.getenv("READER_DAEMON", "./nfcreader/nfcreader")
open_door_script = os.getenv("OPEN_DOOR_SCRIPT", "./open-door")
card_id_pattern = re.compile("(0x[a-f0-9]+)", re.IGNORECASE)
authorized_cards = []

def reload_cards():
  try:
    # Strip away auth part of URL since openurl interprets everything after ':' as a port number
    parsed = urlparse(authorized_cards_url)

    # Rebuild URL without auth
    url = str.format("{0}://{1}/{2}", parsed.scheme, parsed.hostname, parsed.path)
    request = Request(url)

    # Add auth part again manually
    auth_bytes = b64encode(bytes(parsed.username + ":" + parsed.password, "ascii"))
    request.add_header("Authorization", "Basic " + auth_bytes.decode("ascii"))

    log.debug("Downloading new card data")
    with urlopen(request) as req:
      log.debug("Request successful")
      data = b''
      try:
        data = json.loads(req.read().decode("utf-8"))
      except json.decoder.JSONDecodeError as e:
        log.error('Failed to deserialize JSON string')
      
      key = "card_number"
      tmp = []
      for user in data:
        if key in user and len(user[key]) > 0:
          tmp.append(user[key])

      # In case of auth source server errors, don't overwrite old list if no data was found
      if len(tmp) == 0:
        log.debug("Downloaded list contained 0 cards. Keeping existing list.")
        return

      # Update list of cards
      old_len = len(authorized_cards)
      authorized_cards.clear()
      authorized_cards.extend(tmp)
      log.info("Reloaded authorized cards list (before: %d, now: %d)" % (old_len, len(authorized_cards)))
      log.debug(authorized_cards)
  except HTTPError as err:
    log.error("Failed to download new card data: %s" % err)
    log.info("Using existing list. No updates made.")
  except ValueError as err:
    log.error("Invalid URL for authorized cards")
    # Exit with failure
    sys.exit(1)
  except Exception as err:
    log.error("Failed to download new card data.")
    log.error(traceback.format_exc())

def auth_card(card_id):
  return authorized_cards.count(card_id) > 0

def open_door():
  with Popen([open_door_script]) as proc:
    try:
      proc.wait(timeout=10)
    except TimeoutExpired:
      log.error('Timeout exceeded while waiting for door to open')
    return proc.returncode == 0

if __name__ == "__main__":
  if not authorized_cards_url:
    log.error("Missing URL for authorized cards")
    sys.exit(1)

  reload_cards()

  # Open stream in line buffered text mode
  with Popen([reader_daemon], stdout=PIPE, bufsize=1, universal_newlines=True) as proc:
    # TODO: pending rename
    for line in iter(proc.stdout.readline, ''):
      log.debug('nfcreader: %s' % line)
      search = re.search(card_id_pattern, line)
      if search is None:
        log.debug("No card id matched in: %s" % line)
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

