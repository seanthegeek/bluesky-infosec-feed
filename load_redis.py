#!/usr/bin/env python

import csv

import atproto_identity.resolver
import requests
import redis
import atproto_identity

from server.logger import logger

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


did_resolver = atproto_identity.resolver.HandleResolver()

LISTS = [{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/lists/keywords.txt",
    "filename": "lists/keywords.txt",
    "redis_key": "infosec_keywords_regex"
},
{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/lists/keywords_case_sensitive.txt",
    "filename": "lists/keywords_case_sensitive.txt",
    "redis_key": "infosec_keywords_case_sensitive_regex"
},
{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/lists/keywords_vendors.txt",
    "filename": "lists/keywords_vendors.txt",
    "redis_key": "infosec_keywords_vendors_regex"
},
{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/lists/ignore_keywords.csv",
    "filename": "lists/ignore_keywords.csv",
    "redis_key": "infosec_keywords_ignore_keywords_regex"
},
{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/lists/ignore_users.csv",
    "filename": "lists/users.csv",
    "redis_key": "infosec_users_regex"
}
]


def _create_regex_string(input_str: str):
    regex_str = r""
    for keyword in input_str.splitlines():
        keyword = keyword.rstrip()
        if len(keyword) == 0:
            continue
        regex_str += rf"\b{keyword}\b|"
    regex_str = regex_str.rstrip("|")
    return regex_str


def load_redis(url:str, filename:str, redis_key:str):
    value = ""
    try:
        keywords_response = requests.get(url)
        keywords_response.raise_for_status()
        value = keywords_response.text
    except Exception as e:
        logger.error(f"Failed to download {url} - {e}. Falling back to local file {filename}.")
        with open(filename) as keywords_file:
                value = keywords_file.read()
    
    if filename.lower().endswith("users.csv"):
        user_csv = csv.DictReader(value,
                                  fieldnames=["handle", "reason"])
        for row in user_csv:
            dids = []
            handle = row["handle"].lstrip("@")
            did = did_resolver.resolve(handle)
            if did:
                dids.append(did)
        value = ",".join(dids)
    elif filename.lower() == "ignore_keywords.csv":
        ignore_keywords_csv = csv.DictReader(value,
                                             ["regex", "reason"])
        value = ""
        for row in ignore_keywords_csv:
            value+= ignore_keywords_csv["regex"]
        value = value.strip()

    else:
        value = _create_regex_string(value)
    r.set(redis_key, value)


def main():
    for keyword_list in LISTS:
        load_redis(keyword_list["url"], keyword_list["filename"],
                   keyword_list["redis_key"])


if __name__ == "__main__":
    main()
