# A better infosec stream for Bluesky

One of the unique features of [Bluesky](https://bsky.social) is the ability for anyone to write a program that takes in the firehose of posts and updates from the entire platform, do some analysis, and then return a feed of posts that Bluesky users can use. That way, users can choose which algorithms/feeds they like.

I decided to create my own feed. I wasn't sure what the results would look like. It could have been terrible. But, with a little trial and error, I've managed to create an infosec feed that I like better than any other. I hope you like it too. No, seriously, click the like button at [the top of the feed](https://bsky.app/profile/seanthegeek.net/feed/infosec), please. That helps others find this when they search for an infosec feed.

I've found that Bluesky feeds are best viewed on [deck.blue](https://deck.blue), a third-party web client for Bluesky that organizes feeds into aut-refreshing columns, Tweetdeck-style.

## Post criteria

To be included in this feed, a Bluesky post meet the following criteria:

- Must be a new post
- Must not be a reply
  - Reply posts display the whole thread in the feed, taking up too much room
  - Reply posts also were also generally unrelated to infosec
- The post text must contain one or more [keywords](https://github.com/seanthegeek/bluesky-infosec-feed/blob/main/keywords.txt) and/or [case-sensitive keywords](https://github.com/seanthegeek/bluesky-infosec-feed/blob/main/keywords_case_sensitive.txt)
  - The keyword must be included as a full word, not a part of a word

Most keywords are not case-sensitive. However, some words have different meanings when capitalized. For example, in infosec, the acronym APT means Advanced Persistent Threat. However, apt is also [a word in English](https://www.merriam-webster.com/dictionary/apt) meaning suitable or appropriate. Likewise, in infosec the acronym BEC means Business Email Compromise, but Bec is a shorthand for Rebecca, Becca, or because.

Some words like exploit, exploited, and vulnerability are also used in posts related to human rights, criminal justice, or politics, so those posts may occasionally appear in this infosec feed. Phish is is a malicious email and [a band](https://en.wikipedia.org/wiki/Phish) from 1983. Breach is also also a verb that describes whales surfacing from water. You get the idea.

## Architecture

[`load_regex.py`](https://github.com/seanthegeek/bluesky-infosec-feed/blob/main/load_regex.py) downloads the keyword lists from GitHub, converts them into regex patterns, and stores the stores the regex pattern regex strings into a [Redis](https://redis.io/) in-memory cache. A `systemd` timer is used to run `load_regex.py` every minute.

The [`server/`](https://github.com/seanthegeek/bluesky-infosec-feed/tree/main/server) directory contains a [Flask](https://flask.palletsprojects.com/en/stable/) application based on the [MarshalX/bluesky-feed-generator]( MarshalX/bluesky-feed-generator) GitHub project that collects matching posts from the Bluesky firehose and stores them in a SQLlite database on disk. When someone visits the Infosec feed, the Flask application provides the post details that are needed for the Bluesky client to populate the feed.

The filter for posts is located in [`server/data_filter.py`](https://github.com/seanthegeek/bluesky-infosec-feed/blob/main/server/data_filter.py). I have modified this filter so that it reads the regex strings from Redis each time it filters a post. That way, keywords can be updated using a `git` commit, and the Flask application will always use the latest list of keywords without needing to restart the service or worry about file contention race conditions. This ensures that there is no downtime and missed posts when keywords are changed.

The Flask app in executed as a `systemd` service to ensure that it runs on boot after the Redis service starts and is always restarted in the event of a crash. The Flask app is served by [`waitress`](https://flask.palletsprojects.com/en/stable/deploying/waitress/), which sits behind a NGINX reverse proxy.

Everything runs on a Digital Ocean Droplet with 2 GB of RAM, 2 shared vCPU, and 50 GB of SSD storage for a cost of $12/month. Only 377 MB of RAM and 2.5 GB of storage is in use. I wish Digital Ocean had a cheaper  option with 2 vCPUs and less RAM.

## Pull Requests are welcome

If you think keywords should be added or removed, or would like to change the algorithm, feel free to submit a Pull Request (PR) for me to consider merging.
