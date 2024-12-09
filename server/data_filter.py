import datetime
import re
from collections import defaultdict

from atproto import models

from server.logger import logger
from server.database import db, Post

import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def is_archive_record(record):
    # Sometimes users will import old posts from Twitter/X which con flood a feed with
    # old posts. Unfortunately, the only way to test for this is to look an old
    # created_at date. However, there are other reasons why a post might have an old
    # date, such as firehose or firehose consumer outages. It is up to you, the feed
    # creator to weigh the pros and cons, amd and optionally include this function in
    # your filter conditions, and adjust the threshold to your liking.
    #
    # See https://github.com/MarshalX/bluesky-feed-generator/pull/21

    archived_threshold = datetime.timedelta(days=1)
    created_at = datetime.datetime.fromisoformat(record.created_at)
    now = datetime.datetime.now(datetime.UTC)
    return now - created_at > archived_threshold


def include_post(author, record):
    keywords_regex_str = r.get("infosec_keywords_regex")
    case_sensitive_regex_str = r.get("infosec_keywords_case_sensitive_regex")
    vendors_regex_str = r.get("infosec_keywords_vendors_regex")
    ignore_keywords_regex_str = r.get("infosec_keywords_ignore_regex")
    user_dids_str = r.get("infosec_user_dids")
    ignore_user_dids_str = r.get("infosec_ignore_user_dids")
    
    user_dids = []
    if user_dids_str is not None:
        user_dids = user_dids_str.split(",")
    ignore_user_dids = []
    if ignore_user_dids_str is not None:
        ignore_user_dids = ignore_user_dids_str.split(",")

    if record.reply:
        # Reply posts show the whole thread, and show too many unrelated posts
        return False
    if is_archive_record(record):
        return False
    if author in ignore_user_dids:
        return False
    if author in user_dids:
        return True
    if ignore_keywords_regex_str is not None:
        if len(re.findall(ignore_keywords_regex_str, record.text, re.IGNORECASE)) > 0:
            return False

    matches = []
    if keywords_regex_str is not None:
        matches += re.findall(keywords_regex_str, record.text, re.IGNORECASE)
    if case_sensitive_regex_str is not None:
        matches += re.findall(case_sensitive_regex_str, record.text)
    if vendors_regex_str is not None:
        matches+= re.findall(vendors_regex_str, record.text, re.IGNORECASE)

    if len(matches) > 0:
        return True

    return False

def operations_callback(ops: defaultdict) -> None:
    # Here we can filter, process, run ML classification, etc.
    # After our feed alg we can save posts into our DB
    # Also, we should process deleted posts to remove them from our DB and keep it in sync

    posts_to_create = []
    for created_post in ops[models.ids.AppBskyFeedPost]['created']:
        author = created_post['author']
        record = created_post['record']

        if include_post(author,  record):
            reply_root = reply_parent = None
            if record.reply:
                reply_root = record.reply.root.uri
                reply_parent = record.reply.parent.uri

            post_dict = {
                'uri': created_post['uri'],
                'cid': created_post['cid'],
                'reply_parent': reply_parent,
                'reply_root': reply_root,
            }
            logger.debug(record.text)
            posts_to_create.append(post_dict)

    posts_to_delete = ops[models.ids.AppBskyFeedPost]['deleted']
    if posts_to_delete:
        post_uris_to_delete = [post['uri'] for post in posts_to_delete]
        Post.delete().where(Post.uri.in_(post_uris_to_delete))
        logger.debug(f'Deleted from feed: {len(post_uris_to_delete)}')

    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.debug(f'Added to feed: {len(posts_to_create)}')
