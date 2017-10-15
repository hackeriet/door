#!/usr/bin/env python3

from subprocess import Popen, PIPE
import re

def open_door():
  with Popen(["./open-door"]) as proc:
    proc.wait()
    return proc.returncode == 0

# TODO: Do authentication sequence here
def auth_card(card_id):
  with Popen(["./auth-card", card_id], stdout=PIPE) as proc:
    proc.wait()
    return proc.returncode == 0

with Popen(["barbatos/barbatos"], stdout=PIPE) as proc:
  for line in iter(proc.stdout.readline, b''):
    card_id = re.findall("0x[a-f0-9]+$", line.decode('utf8'), flags=re.I)
    # On the very first iteration the subprcess outputs
    # a status message which will not match the regex.
    # Will have to check length, or do a .match_count() call first
    if len(card_id) > 0:
      card_id = card_id[0]
      print("Card read: %s" % card_id)
      if auth_card(card_id):
        open_door():

