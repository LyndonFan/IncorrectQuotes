from typing import Any, List, Optional, Dict, Tuple
import asyncio
from datetime import datetime
import json, re, time
from new_scrapper import right_format, scrap_url


async def async_scrap_url(
    url: str, last_visited: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    if not right_format(url):
        return []
    res = await scrap_url(url, last_visited)
    return res


async def async_scrap_urls(
    inp: List[Tuple[str, Optional[datetime]]]
) -> List[Dict[str, Any]]:
    input_coroutines = [async_scrap_url(*xs) for xs in inp]
    ress = await asyncio.gather(*input_coroutines, return_exceptions=True)
    res = [x for xs in ress for x in xs]
    return res


if __name__ == "__main__":
    with open("links.json", "r") as f:
        jsn = json.load(f)
    inputs: List[Tuple[str, Optional[datetime]]] = [
        (r["url"], (r["last_visited"] if "last_visited" in r else None)) for r in jsn
    ]
    results: List[Dict[str, Any]] = asyncio.get_event_loop().run_until_complete(
        async_scrap_urls(inputs)
    )
    with open("new_scrapped_data.json", "w+") as f:
        json.dump(results, f)