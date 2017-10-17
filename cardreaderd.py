#!/usr/bin/env python3
import os, re, logging
from subprocess import Popen, PIPE

logging.basicConfig(level='DEBUG')
log = logging.getLogger(__name__)

testing = os.getenv('TESTING', False)
card_id_pattern = re.compile('(0x[a-f0-9]+)', re.IGNORECASE)
reader_daemon = './barbatos/barbatos' if not testing else './test/reader-daemon'
authorized_cards = os.getenv('AUTHORIZED_CARDS', 'test/card_ids.txt')

def auth_card(card_id):
  with open(authorized_cards, encoding='utf-8') as fd:
    for i, line in enumerate(fd):
      if card_id == line.rstrip():
        return True
    return False

def open_door():
  with Popen(["./open-door"]) as proc:
    proc.wait()
    return proc.returncode == 0

with Popen([reader_daemon], stdout=PIPE) as proc:
  for line in iter(proc.stdout.readline, b''):
    match = re.search(card_id_pattern, line.decode('utf-8'))
    # Extract the card ID from the line
    if match and match.group():
      card_id = match.group()
      if auth_card(card_id):
        log.info('Card %s is authorized' % card_id)
        if open_door():
          log.info('Door opened')
        else:
          log.error('Failed to open door')
      else:
        log.warning('Card %s is not authorized' % card_id)

