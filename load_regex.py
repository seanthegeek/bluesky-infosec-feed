#!/usr/bin/env python

import requests
import redis

from server.logger import logger

KEYWORDS_FILE_URL = "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/requirements.txt"

def _create_regex_string(input_str: str):
    regex_str = r""
    for keyword in input_str.splitlines():
        keyword = keyword.rstrip()
        if len(keyword) == 0:
            pass
        regex_str += rf"\b{keyword}\b|"
    regex_str = regex_str.rstrip("|")
    return regex_str

def main():
    keywords_str = ""
    try:
        keywords_response = requests.get(KEYWORDS_FILE_URL)
        keywords_response.raise_for_status()
        keywords_str = keywords_response.text
    except Exception as e:
        logger.error(f"Failed to download {KEYWORDS_FILE_URL} - falling back to local file")
    with open("keywords.txt") as keywords_file:
        keywords_str = keywords_file.read()
    regex_str = _create_regex_string(keywords_str)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.set("infosec_keywords_regex", regex_str)

if __name__ == "__main__":
    main()
