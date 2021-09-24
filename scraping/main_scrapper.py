from scrapper import *

# from process import *
import argparse
import json


def scrapPages(pages, keepTags=True):
    with open("../data/sources.json", "r") as f:
        visited = json.load(f)
    visited_urls = [r["url"] for r in visited]
    try:
        with open("scrapped_data.json", "r") as json_file:
            old_data = json.load(json_file)
    except:
        old_data = []
    for pg in pages:
        try:
            if not (pg["url"] in visited_urls):
                print("Starting to scrap", pg["url"])
                data = scrap(pg["url"], testing=False, headless=True)
                print("Finished scrapping page")
                # quotes = process(data, names_list=pg["ppl"])
                old_data += data
                visited.append(pg)
            else:
                print("Already visited", pg["url"], ". Please call rescrap instead.")
        except Exception as e:
            print(e)
            print("Omitting this url...")
    with open("scrapped_data.json", "w+") as f:
        json.dump(old_data, f, indent=4)
    with open("../data/sources.json", "w+") as f:
        json.dump(visited, f, indent=4)


def rescrap(pages, keepTags=True):
    with open("../data/sources.json", "r") as f:
        visited = json.load(f)
    visited_urls = [r["url"] for r in visited]
    for pg in pages:
        if pg["url"] in visited_urls:
            idx = visited_urls.index(pg["url"])
            visited.pop(idx)
            visited_urls.pop(idx)
    with open("../data/sources.json", "w") as f:
        json.dump(visited, f, indent=4)
    with open("quotes.json", "r") as f:
        quotes = json.load(f)
    quotes = list(
        filter(lambda q: not any(q["url"] == pg["url"] for pg in pages), quotes)
    )
    with open("quotes.json", "w") as f:
        json.dump(quotes, f, indent=4)
    scrapPages(pages, keepTags)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrap quotes from a tumblr page.")
    parser.add_argument(
        "path",
        nargs=1,
        help='path to json of list of quotes. The schema is\n...[{"url":...,"ppl":[...]}]\nThe ppl is list of characters\' names and can be empty.',
    )
    parser.add_argument(
        "-t",
        "--keepTags",
        dest="keepTags",
        action="store_true",
        help="boolean to indicate whether you want to keep the tags of the original post (add this to set to True, add -np / --no-keepTags to set to False)",
    )
    parser.add_argument(
        "-nt", "--no-keepTags", "--no-p", dest="keepTags", action="store_false"
    )
    parser.set_defaults(keepTags=True)
    args = parser.parse_args()
    print("arguments: " + str(args))
    with open(args.path[0], "r") as f:
        jsn = json.loads(f.read())
    scrapPages(jsn, args.keepTags)

