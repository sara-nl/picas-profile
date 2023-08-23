#!/usr/bin/env python3
"""
@author: lnauta
"""

import datetime
import sys
import os
import couchdb
import picasconfig

def getNextIntCDB(db):
    """
    Get next integer for the CouchDB instance. This is used for creating a new token

    @param db: database instance

    @return: (int) value of the next integer that is unused in CouchDB
    """

    i = 0
    while db.get("token_"+str(i)) is not None:
        i+=1

    return i

def addToken(db, jobscript):
    """
    Add a token to the PiCaS database

    @param db: database instance
    @param jobscript: jobscript created by snakemake from the profile template

    @return: job ID as used in PiCaS
    """

    i = getNextIntCDB(db)

    jobscript = open(jobscript, 'r')
    lines = jobscript.readlines()

    token = {
        '_id': 'token_' + str(i),
        'type': 'token',
        'lock': 0,
        'done': 0,
        'hostname': '',
        'scrub_count': 0,
        'exit_code': '',
        'input': lines[0],
        'properties': lines[1],
    }

    db.update([token])
    return i

def get_db():
    """
    Get PiCaS CouchDB database instance

    @return: CouchDB handler
    """
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username,pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db

if __name__ == '__main__':
    # Create a connection to the server
    db = get_db()
    # Load the tokens to the database
    # Eureka: argv[1] is the path to the formatted job script from snakemake!
    jobid = addToken(db, sys.argv[1])
    print(jobid)
