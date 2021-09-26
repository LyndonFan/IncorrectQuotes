from typing import Any, List, Optional, Dict, Tuple, Set
import asyncio
from datetime import datetime
import json, re, time


def can_keep(post: Dict[str, Any]) -> bool:
    if "asking_url" in post or "source_url" in post:
        # first is a Q&A -- hard to extract/format
        # second is reblog
        return False
    if post["trail"] != []:  # possible reblog
        return False


keep_tags: Set[str] = {
    "tags",
    "timestamp",  # so need not "date", which is a string
    "reblogged_from_title",
    "reblogged_from_url",
    "short_url",
    "reblogged_from_name",
    "content",
    "is_nsfw",  # similar to "classification"
    "reblogged_root_url",
    "post_url",
    "reblogged_root_name",
    "blog_name",
    "id_string",  # similar/same as "id"
}

