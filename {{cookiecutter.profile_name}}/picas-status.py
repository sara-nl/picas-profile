#!/usr/bin/env python3
"""
@author: lnauta
"""

import sys
import time
import couchdb
import picasconfig


def get_db():
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username,pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db


STATUS_ATTEMPTS = 20

# try to get status STATUS_ATTEMPTS times
def get_status(jobid):
    for i in range(STATUS_ATTEMPTS):
        db = get_db()
        token = db.get("token_"+str(jobid))
        if token == "":
            raise ValueError(f"Queried PiCaS token {jobid} does not exist.")
        else:
            # token logic here
            if token['lock'] == 0 and token['done'] == 0:
                return 'todo'
            elif token['lock'] > 0 and token['done'] == 0:
                return 'locked'
            elif token['lock'] > 0 and token['done'] > 0:
                if token['exit_code'] == 0:
                    return 'done'
                elif token['exit_code'] != 0:
                    return 'error'
            else:
                raise KeyError(f"Queried PiCaS token {jobid} has inconsistent values in either 'lock', 'done' or 'error_code'")
        return res[jobid]

jobid = sys.argv[1]
status = get_status(jobid)

# the translation from PiCaS status to snakemake status
if status == "done":
    print("success")
elif status == "error":
    print("failed")
elif status == "":
    print("failed")
elif status == "todo":
    print("running")
elif status == "locked":
    print("running")
else:
    print("running")
