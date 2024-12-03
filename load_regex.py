#!/usr/bin/env python

import requests
import redis

from server.logger import logger

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

KEYWORD_LISTS = [{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/keywords.txt",
    "filename": "keywords.txt",
    "redis_key": "infosec_keywords_regex"
},
{
    "url": "https://github.com/seanthegeek/bluesky-infosec-feed/raw/refs/heads/main/keywords_case_sensitive.txt",
    "filename": "keywords_case_sensitive.txt",
    "redis_key": "infosec_keywords_case_sensitive_regex"
}]


def _create_regex_string(input_str: str):
    regex_str = r""
    for keyword in input_str.splitlines():
        keyword = keyword.rstrip()
        if len(keyword) == 0:
            pass
        regex_str += rf"\b{keyword}\b|"
    regex_str = regex_str.rstrip("|")
    return regex_str


def load_regex(url, filename, redis_key):
    keywords_str = ""
    try:
        keywords_response = requests.get(url)
        keywords_response.raise_for_status()
        keywords_str = keywords_response.text
    except Exception as e:
        logger.error(f"Failed to download {url} - falling back to local file {filename}")
    with open(filename) as keywords_file:
        keywords_str = keywords_file.read()
    regex_str = _create_regex_string(keywords_str)
    r.set(redis_key, regex_str)


def main():
    for keyword_list in KEYWORD_LISTS:
        load_regex(keyword_list["url"], keyword_list["filename"],
                   keyword_list["redis_key"])


if __name__ == "__main__":
    main()
