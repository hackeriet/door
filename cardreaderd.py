#!/usr/bin/env python3
import logging
from subprocess import Popen, PIPE
import re

logging.basicConfig(level='DEBUG')
log = logging.getLogger(__name__)

card_id_pattern = re.compile("(0x[a-f0-9]+)", re.IGNORECASE)
authorized_cards = './card_ids.txt'
reader_daemon = './barbatos/barbatos'
#reader_daemon = './test/reader-daemon'

def open_door():
  with Popen(["./open-door"]) as proc:
    proc.wait()
    return proc.returncode == 0

def auth_card(card_id):
  with open(authorized_cards, encoding='utf-8') as fd:
    for i, line in enumerate(fd):
      if card_id == line.rstrip():
        return True
    return False

with Popen([reader_daemon], stdout=PIPE) as proc:
  for line in iter(proc.stdout.readline, b''):
    match = re.search(card_id_pattern, line.decode('utf-8'))
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

