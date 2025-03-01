#!/usr/bin/env bash

/opt/blueskyinfosecfeed/bluesky-infosec-feed/venv/bin/python3 load_redis.py
$rm -f feed_database.db*
