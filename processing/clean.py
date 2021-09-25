import numpy as np
import pandas as pd
import re, json, html

REPLACEMENTS = {
    "incorrect": ["inncorrect", "incorect", "inncorect"],
    "'": ["\u2018", "\u2019", "\u2032"],
    "...": ["\u2026"],
    '"': ["\u201c", "\u201d"],
    "-": ["\u2013", "\u2014"],
    "source": ["sorce"],
    "source:": ["source;"],
    "quote": ["qoute"],
    "Person": ["Parson"],
    " ": ["\xa0"],
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


def _html_to_quote(q, preserve_tags=False):
    if q.count("<a href=") > 1:
        return ""
    q = re.sub("<a href.*", "", q)
    q = re.sub("</?div.*?>", "\n", q)
    q = re.sub("(</p>(\n)*<p.*?>)|(</span>(\n)*<span.*?>)", "\n", q)
    q = re.sub("\n+", "\n", q)
    if not preserve_tags:
        q = re.sub("<.*?>", "", q)
    q = html.unescape(q)
    return q.strip()


def _is_quote(q):
    return (len(q) - q.count("\n")) / (q.count("\n") + 1) < 500 and (bool)(
        re.search("^((\*[^\n]+\*|\[[^\n]+\]|[A-Za-z0-9][^\n:]*:[^\n]*)(\n|))+$", q)
    )
    # check for each line, the only colon should NOT be inside parenthesis


def clean(df):
    if type(df) is not pd.DataFrame:
        df = pd.DataFrame(df)
    df = df[
        [
            (not any((bool)(re.search("^#not.*quote$", t)) for t in ts))
            for ts in df.original_tags
        ]
    ]
    df["quote"] = df["quote"].apply(lambda x: re.sub("<a href=.*</a>$", "", x))
    df["raw"] = df["quote"]
    df["quote"] = df["quote"].apply(_html_to_quote)
    df = df[df["quote"].apply(_is_quote)]
    return df
