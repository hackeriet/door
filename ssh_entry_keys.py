#!/usr/bin/env python
import json
import requests
import subprocess
import pathlib
import grp


#try:

GROUP_NAMES = "hackeriet-members"
LOCAL_KEYS = pathlib.Path("/home/entry/.ssh/authorized_keys")
AUTH_TOKEN = pathlib.Path("/etc/door-sso-token").read_text().strip()


def get_sso_members() -> set[str]:
    try:
        data = requests.get(
            "https://idp.hackeriet.no/v1/group/{GROUP_NAMES}",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        ).json()
        return set(data["attrs"]["member"])
    except:
        return set()


def get_local_members() -> set[str]:
    return set(grp.getgrnam(GROUP_NAMES).gr_mem)


print(f"# Local keys in {LOCAL_KEYS}")
print(LOCAL_KEYS.read_text())


for member in get_local_members() | get_sso_members():
    print(f"# SSO keys for {member}")
    print(subprocess.run(
        ["/usr/sbin/kanidm_ssh_authorizedkeys", member],
        text="utf-8",
        capture_output=True,
    ).stdout)

#except Exception as e:
#    with open("/tmp/wtflol", "w") as fh:
#        import traceback
#        fh.write("".join(traceback.format_exception(e)))
