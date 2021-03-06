from typing import Any, List, Dict, Optional
import requests
import json, re, time
from fake_useragent import UserAgent
from datetime import datetime
import sys, os
import asyncio

curr_folder: str = os.path.dirname(__file__)


def right_format(x: str) -> bool:
    return re.match("^https:\/\/[^\.]*\.tumblr\.com(\/(archive\/?)?)?$", x)


# last_visited is timestamp
async def scrap_url(
    url: str, last_visited: Optional[float] = None
) -> List[Dict[str, Any]]:
    assert right_format(url), f"The input isn't a proper link to a tumblr blog:\n{url}"
    ua = UserAgent()
    with open(os.path.join(curr_folder, "new_scrapping_secrets.json"), "r",) as f:
        headers: Dict[str, str] = json.load(f)
    headers["user-agent"] = ua.random
    headers["origin"] = url
    headers["referer"] = re.sub("/+$", "/", url + "/")

    domain: str = url.split(".tumblr.com")[0].replace("https://", "")

    params: Dict[str, str] = {
        "fields[blogs]": "posts,title,name",
        "npf": "true",
        "reblog_info": "true",
    }

    care_date: bool = True if last_visited is not None else False
    if care_date:
        target_timestamp: float = last_visited
        oldest_timestamp: float = target_timestamp + 1

    posts: List[Dict[str, Any]] = []
    new_posts: List[Dict[str, Any]] = [{}]

    while len(new_posts) > 0:
        if care_date and target_timestamp > oldest_timestamp:
            break
        params["offset"] = str(len(posts))
        response = requests.get(
            f"https://api.tumblr.com/v2/blog/{domain}/posts",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            print(url, "failed:")
            print("Got status code", response.status_code)
            print(response.text)
            return {}
        new_posts = response.json()["response"]["posts"]  # length <= 20 by API
        if care_date and len(new_posts) > 0:
            oldest_timestamp = min(p["timestamp"] for p in new_posts)
            if oldest_timestamp < target_timestamp:
                new_posts = [p for p in new_posts if p["timestamp"] >= target_timestamp]
        posts += new_posts
        await asyncio.sleep(0.5)
    print("Finished scraping", url)
    return posts


if __name__ == "__main__":
    args: List[str] = sys.argv[1:]
    actual_args: List[str] = []
    for x in args:
        if os.path.exists(x) and x.split(".")[-1] == "json":
            with open(x, "r") as f:
                jsn = json.load(f)
            try:
                urls = [r["url"] for r in jsn]
                actual_args += [url for url in urls if right_format(url)]
            except:
                pass
        else:
            if right_format(x):
                actual_args.append(x)
    for u in actual_args:
        print("Scraping", u, "...")
        try:
            posts = asyncio.get_event_loop().run_until_complete(scrap_url(u))[0]
            if len(posts) > 0:
                domain = posts[0]["blog_name"].replace(" ", "_").replace("/", "-")
                with open(f"../_testing/{domain}.json", "w+") as f:
                    json.dump(posts, f, indent=4)
        except Exception as e:
            print(e)
            print("Failed to load posts for", u)

# Note: reblogged posts have a non-empty "trail"...
