from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import requests
import re
import time
import json
import sys

REPLACEMENTS = {
    "incorrect": ["inncorrect", "incorect", "inncorect"],
    "'": ["\u2018", "\u2019", "\u2032"],
    "...": ["\u2026"],
    '"': ["\u201c", "\u201d"],
    "-": ["\u2013", "\u2014"],
    "source": ["sorce"],
    "source:": ["source;"],
    "quote": ["qoute"],
}

AVOID_WORDS = [
    "source",
    "incorrect",
    "blank",
    "template",
    "prompt",
    "quote",
    "people",
    "person",
    "dialogue",
    "submitted",
    "writing",
    "ABC",
    "drawing",
    "submission",
    "funny",
]


def correct_spellings(txt):
    for cor in REPLACEMENTS:
        for mis in REPLACEMENTS[cor]:
            txt = txt.replace(mis, cor)
    return txt


def scrap(url, testing=True, headless=True, keepTags=True):
    chrome_options = ChromeOptions()
    chrome_options.headless = headless
    driver = webdriver.Chrome("./chromedriver", options=chrome_options)
    driver.get(url)
    title = driver.title
    print("On", title, "page")
    time.sleep(3)
    SCROLL_PAUSE_TIME = 3
    MAX_REPEAT_SCROLLS = 0 if testing else 2
    scroll_count = 0
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while scroll_count < MAX_REPEAT_SCROLLS:
        print(last_height, end="...")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_count += 1
        else:
            scroll_count = 0
        last_height = new_height
    quotes = driver.find_elements_by_class_name("post")
    print(len(quotes), "posts found")
    if testing:
        quotes = quotes[:5]
        for i, q in enumerate(quotes):
            print("Post", i + 1, ":")
            print(q.text)
            print()

    temp_quote = quotes[0]
    part = ""
    for poss_part in ["body-text", "post-content", "post"]:
        try:
            test_quote = temp_quote.find_element_by_class_name(poss_part).text
            part = poss_part
            break
        except:
            pass
    if part == "":
        print("Can't found corresponding class which contains the quote")
        exit()

    def extract(elem):
        parent = elem.find_element_by_xpath("..")
        repost = parent.find_elements_by_class_name("reblog_sm")
        if len(repost) > 0:
            if testing:
                print("Found repost")
            return {}
        image = parent.find_elements_by_class_name("img")
        if len(image) > 0:
            if testing:
                print("Found image")
            return {}
        try:
            quote = elem.find_element_by_class_name(part).text
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print("Omitting this element:")
            print(elem)
            return {}
        if not (bool)(re.match("(\[.+?\]\n)?[A-Za-z0-9 ,]+:", quote)):
            if testing:
                print("Not a quote")
            return {}
        if any(s in quote for s in ["Image description", "IMAGE DESCRIPTION"]):
            if testing:
                print("Post is an image")
            return {}
        tags = elem.find_elements_by_class_name("tag-link")
        tags = ["#" + correct_spellings(t.text) for t in tags]
        if not any("incorrect" in t for t in tags):
            if testing:
                print("Irrelevant, tags =", tags)
            return {}
        source_tags = list(filter(lambda t: "source" in t, tags))
        sources = ["tubmlr ({})".format(title)]
        for s in source_tags:
            if ": " in s:
                s = s.split(": ")[1]
                if not (s == "" or s[0] == "?" or s == "tumblr"):
                    sources.append(s)

        res = {
            "quote": correct_spellings(quote),
            "source": sources,
            "url": url,
        }
        if keepTags:
            remaining_tags = list(
                filter(
                    lambda t: not (
                        any(w in t.lower() for w in AVOID_WORDS) or len(t) <= 4
                    ),
                    tags,
                )
            )
            res["original_tags"] = remaining_tags
        return res

    quotes = list(filter(lambda d: not (d == {}), [extract(q) for q in quotes]))
    print(len(quotes), "quotes extracted")
    # with open("quotes_from_{}.json".format(title.replace(" ","_").replace("/","_")),"w+") as f:
    #     json.dump(quotes,f,indent=4)
    driver.close()
    driver.quit()
    return quotes


if __name__ == "__main__":
    url = "https://incorrectquoteprompts.tumblr.com/"
    scrap(url, testing=True)

