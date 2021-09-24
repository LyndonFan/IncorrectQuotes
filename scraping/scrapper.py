from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import sys

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


def scrap(url, testing=True, headless=True, keepTags=True):
    if not re.search("\.com/archive$", url):
        url += ("/" if url[-1] != "/" else "") + "archive"
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
        sys.stdout.flush()  # doesn't wait for scrolling to finish?
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
        if testing:
            break
    print("Finished scrolling", file=sys.stderr)

    all_posts = driver.find_element_by_xpath('//*[@id="base-container"]/div[2]/div[2]')
    quotes = []
    for month in all_posts.find_elements_by_xpath("./div"):
        posts = month.find_element_by_xpath(".//div")
        quotes += posts.find_elements_by_xpath("./div")
    print(len(quotes), "posts to process")

    def extract(elem):
        # print("-" * 40)
        # print(elem.get_attribute("innerHTML"), file=sys.stderr)
        content = elem.find_element_by_xpath(".//div[1]")
        info = elem.find_element_by_xpath(".//a")
        # print(info.get_attribute("innerHTML"))
        try:
            quote = content.get_attribute("innerHTML")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print("Omitting this element:")
            print(elem)
            return {}
        if "<img" in quote:
            if testing:
                print("Found image")
            return {}
        # # leave cleaning to be done in another file
        # quote = re.sub("</?div.*?>", "", quote)
        # text_only = re.sub("<.*?>", "", quote)
        # if not (bool)(re.match("(\[.+?\]\n)?[A-Za-z0-9 ,]+:", text_only)):
        #     if testing:
        #         print("Not a quote")
        #     return {}
        # del text_only
        try:
            tags = info.find_element_by_xpath(".//div[2]")
        except NoSuchElementException:
            print("You might want to take a look at the following for", url)
            print(info.get_attribute("innerHTML"))
            try:
                tags = info.find_element_by_xpath(".//div")
            except NoSuchElementException:
                print("Failed to find tags")
                tags = False
        tags = tags.get_attribute("innerHTML") if tags else ""
        tags = re.split(" (?=#)", tags)
        # # leave cleaning to be done in another file
        # tags = [correct_spellings(t) for t in tags]
        # if not any("incorrect" in t for t in tags):
        #     if testing:
        #         print("Irrelevant, tags =", tags)
        #     return {}
        source_tags = list(filter(lambda t: "source" in t, tags))
        sources = ["tubmlr ({})".format(re.sub(": Archive$", "", title))]
        for s in source_tags:
            if ": " in s:
                s = s.split(": ")[1]
                if not (s == "" or s[0] == "?" or s == "tumblr"):
                    sources.append(s)
        try:
            date = info.find_element_by_xpath(".//h1").get_attribute("innerHTML")
        except NoSuchElementException:
            print("Couldn't find date")
            date = ""
        res = {
            "quote": quote,
            "source": sources,
            "date": date,
            "url": info.get_attribute("href"),
        }
        if keepTags:
            remaining_tags = list(filter(lambda t: not "source" in t, tags))
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

