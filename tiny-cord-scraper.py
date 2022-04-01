#!/usr/bin/python3
import requests
import json
import time
import os
import logging
import sys
import getopt

# put authorization token here, from devtools network tab .. 
# look for "messages?limit=50", the header with have the 
# Authorization token.
h = {'authorization': os.environ['DIS_TOKEN']} 

# Create logger
logging.basicConfig(filename="tiny-cord-scraper.log", level=logging.DEBUG)
logger = logging.getLogger()

def get_last_messages_from_channel(channel_id, limit, before=0):
    """scape a discord message channel, channel_id is a discord Snowfake of the channel, before is where it left off"""

    # Lets get the block of messages
    if before != 0:
        r = requests.get('https://discord.com/api/v9/channels/' + channel_id + '/messages?limit=' + str(limit) + '&before=' + before, headers=h)
    else:
        r = requests.get('https://discord.com/api/v9/channels/' + channel_id + '/messages?limit=' + str(limit), headers=h)

    # Are we not status code OK?
    if r.status_code != 200:
        logger.error("Got" + str(r.status_code) + "instead of 200")
        return 0 # True

    # Trun text into json and print it
    j = json.loads(r.text)
    before = j[len(j)-1]['id']
    jformatted = json.dumps(j, indent=2)
    print(jformatted)
    
    # Sleep to not get rate limited
    time.sleep(1)

    # If less that 'limit', This will be last
    if len(j) < int(limit):
        return len(j)   # More than 0 records, Not Done, run again

    if(get_last_messages_from_channel(channel_id, limit, before) == 0):
        return 0    # Done!


def printhelp():
    """List out argument usage"""
    print(f"Usage: {sys.argv[0]} [OPTIONS]")
    print(f"      -h, --help       This help display")
    print(f"      -c, --channel    Discord channel_id")
    print(f"      -l, --limit      Limit of records (less than 100)")


def main(argv):
    """Get options and start the program"""
    # defaults
    limit=100
    channel=0

    options = "hc:l:"
    long_options = ["help", "channel=", "limit="]

    try:
        opts, args = getopt.getopt(argv, options, long_options)
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit(2)
        elif opt in ("-c", "--channel"):
            channel = arg
        elif opt in ("-l", "--limit"):
            limit = arg

    if channel == 0:
        printhelp()
        sys.exit(2)

    if int(limit) > 100:
        printhelp()
        sys.exit(2)

    # Print some stats
    #print(f"Channel: {channel} Type: {type(channel)}")
    #print(f"Limit: {limit} Type: {type(channel)}")

    # Keep the time
    start_time = time.time()

    get_last_messages_from_channel(channel, limit)

    # Calculate the run time
    stop_time = time.time()
    dt = stop_time - start_time

    # log and print the stats
    logger.info("Run time {} seconds".format(dt))
    print("Run time {}".format(dt))

# get the last message_id, and spit it out
# to continoue on where you left off. 

if __name__ == "__main__":
    main(sys.argv[1:])

