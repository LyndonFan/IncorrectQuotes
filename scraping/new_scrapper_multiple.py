from typing import Any, List, Optional, Dict, Tuple
import asyncio
from datetime import datetime
import json, re, time
from new_scrapper import right_format, scrap_url
from new_scrapper_preprocess import preprocess


async def async_preprocess(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    res = await preprocess(posts)
    return res


async def async_scrap_url(
    url: str, last_visited: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    if not right_format(url):
        return []
    res = await scrap_url(url, last_visited)
    res = await async_preprocess(res)
    return res


# doesn't matter if preprocess before/after merge
# similarly fast in testing (w/in same magnitude, and < 1e-4 !)
async def async_scrap_urls(
    inp: List[Tuple[str, Optional[float]]]
) -> List[Dict[str, Any]]:
    input_coroutines = [async_scrap_url(*xs) for xs in inp]
    ress = await asyncio.gather(*input_coroutines, return_exceptions=True)
    res = [x for xs in ress for x in xs]
    return res


if __name__ == "__main__":
    with open("links.json", "r") as f:
        jsn: List[Dict[str, Any]] = json.load(f)
    inputs: List[Tuple[str, Optional[float]]] = [
        (r["url"], (r["last_visited"] if "last_visited" in r else None)) for r in jsn
    ]
    results: List[Dict[str, Any]] = asyncio.get_event_loop().run_until_complete(
        async_scrap_urls(inputs)
    )
    with open("new_scrapped_data.json", "w+") as f:
        json.dump(results, f)
    with open("../data/sources.json", "r") as f:
        sources = json.load(f)
    rev_lookup: Dict[str, int] = {r["url"]: i for i, r in enumerate(sources)}
    now_timestamp: float = datetime.now().timestamp()
    for r in jsn:
        u: str = r["url"]
        if r["url"] in rev_lookup:
            sources[rev_lookup[u]]["last_visited"] = now_timestamp
        else:
            sources.append(
                {"url": u, "last_visited": now_timestamp, "universe": r["universe"]}
            )
    with open("../data/sources.json", "w") as f:
        json.dump(sources, f, indent=4)

