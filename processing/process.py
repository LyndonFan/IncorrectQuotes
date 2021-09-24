import json
import numpy as np
import pandas as pd
import re
from Levenshtein import distance as word_dist
from disjoint_set import DisjointSet

pd.set_option("display.max_rows", 999)

not_characters = [
    "also",
    "not",
    "someone",
    "random",
    "no one",
    "everyone",
    "anybody",
    "anyone",
    "any",
    "entire",
    "me",
    "some",
    "all",
    "most",
    "person",
    "my",
]
pattern = "(^a )|\!|'s|" + "((^| )(" + "|".join(not_characters) + ")($| ))"


def _detect_characters(quotes):
    names_set = set([])
    for q in quotes:
        for l in q.split("\n"):
            if ":" in l:
                speakers = re.split(" and | \& ", l.split(":")[0])
                assert not None in speakers, "Invalid quote: \n%s" % q
                speakers = set(map(lambda x: x.split(",")[0].strip(), speakers))
                names_set = names_set.union(set(speakers))
    names_set = set(map(lambda x: x.strip(), names_set))
    names_set = set(filter(lambda x: not re.search(pattern, x.lower()), names_set))
    return names_set


def _clean_characters(quotes, names_list):
    names_df = pd.DataFrame(names_list, columns=["name"])
    names_df = names_df[names_df.name.apply(lambda x: x.count(" ") < 3)]
    names_df["name_lower"] = names_df["name"].apply(lambda x: x.lower())
    lower_once = lambda x: names_df["name_lower"].value_counts()[x] == 1
    names_df = names_df[
        (names_df.name.apply(lambda x: x != x.lower()))
        | (names_df.name_lower.apply(lower_once))
    ]
    not_subst = lambda x: not any(
        x != s and s.lower() in x.lower() for s in names_df.name
    )
    names_df = names_df[
        (names_df.name.apply(lambda x: x.count(" ") < 2))
        | (names_df.name.apply(not_subst))
    ]
    to_removes = []
    for n in names_df.name_lower:
        to_remove = False
        for i in range(len(names_df.name) - 1):
            if to_remove:
                break
            m1 = names_df.name_lower.iloc[i]
            if m1 == n:
                continue
            for j in range(i + 1, len(names_df.name)):
                m2 = names_df.name_lower.iloc[j]
                if m2 == n:
                    continue
                to_remove = m1 in n and m2 in n
                if to_remove:
                    break
        to_removes.append(to_remove)
    names_df = names_df[[not x for x in to_removes]]
    names_df["count"] = names_df.name_lower.apply(
        lambda x: sum(q.lower().count(x) for q in quotes)
    )
    names_df = names_df.drop(columns="name_lower")
    names_df = names_df.sort_values(by=["count"], ignore_index=True)
    return names_df


NOT_TAGS = ["source", "quote", " i ", "[", "?"]

# DON'T GROUP -- leave this to be done manually


def detect_characters(quotes, tags=None):
    print("Detecting characters...")
    potential_characters = _detect_characters(quotes)
    print("Removing non-characters...")
    names_df = _clean_characters(quotes, potential_characters)
    names_list = set(names_df.name)
    print(len(names_df), "characters found!")
    print(names_df)
    del_names = [
        input(
            "Do you have any names to remove? Input them on the next line, separating them by a new line. When there aren't any more characters you want to remove, just press Enter.\n"
        )
    ]
    while del_names[-1] != "":
        del_names.append(input())
    for i in range(len(del_names)):
        if re.match("\-?[0-9]+", del_names[i]):
            del_names[i] = names_df.name.iloc[int(del_names[i])]
    names_list = names_list.difference(set(del_names[:-1]))
    new_names = [
        input(
            "Do you have any names to add? Input them on the next line, separating them by a new line. When there aren't any more characters you want to add, just press Enter.\n"
        )
    ]
    while new_names[-1] != "":
        new_names.append(input())
    names_list = names_list.union(set(new_names[:-1]))
    return list(names_list)


def idx(main, *substrs):
    i = len(main)
    for s in substrs:
        if len(s) > 2 and s in main:
            i = min(i, main.index(s))
    return i


# TODO: Instead of this allow any mix of up/lower case
def uplower(s):
    return [s, s.upper(), s.lower()] if len(s) > 1 else [s.upper()]


enders = ["-", ".", ":", "!", ",", " ", "*", "?", "'", '"', "\n", ")", "]"]
enders_regex = "\-|\.|\:|\!|,| |\*|\?|'|\"|\n|\)|\]"


def _process(df, names_list=[]):
    if names_list == []:
        names_list = detect_characters(list(df.quote), list(df.original_tags))
    for i in range(len(names_list)):
        if type(names_list[i]) == str:
            names_list[i] = [names_list[i]]
    print("List of characters (one per row, each row has all their aliases):")
    for n_list in names_list:
        print(n_list)

    def _process_quote(quote):
        involved = []
        for person in names_list:
            if any(
                any(idx(quote, *uplower(p + e)) < len(quote) for e in enders)
                for p in person
            ):
                involved.append(person)
        involved.sort(key=lambda ppl: min(idx(quote, *uplower(p)) for p in ppl))
        q = quote
        for i, ppl in enumerate(involved):
            for p in ppl:
                for s in uplower(p):
                    q = re.sub(f"\[{s}\]|\({s}\)", s, q)
                    q = q.replace("(" + s + ")", s)
                for s in uplower(p):
                    q = re.sub(f"^{s}", "{" + str(i) + "}", q,)
                    q = re.sub(
                        f"(?<={enders_regex}){s}(?={enders_regex})",
                        "{" + str(i) + "}",
                        q,
                    )
        return pd.Series([q, len(involved), involved])

    # # try
    # df.loc[:,"original_ppl"] = np.nan
    # df.loc[:,"num_ppl"] = np.nan
    df["original_ppl"] = np.nan
    df["num_ppl"] = np.nan
    df[["quote", "num_ppl", "original_ppl"]] = df["quote"].apply(_process_quote)

    return df


def add_universe(df):
    with open("../data/universes.json", "r") as f:
        universes = json.load(f)
    with open("../data/sources.json", "r") as f:
        sources = json.load(f)
    sources = {r["url"]: r for r in sources}
    if type(df) == json:
        df = pd.DataFrame(df)
    if not "universe" in df.columns:
        df["universe"] = df["url"].apply(
            lambda x: sources["/".join(x.split("/")[:3]) + "/"]["universe"]
        )
    return df, universes


def process(df):
    df, universes = add_universe(df)
    new_dfs = []
    for u in df["universe"].unique():
        print("Universe:", u)
        temp_df = _process(df[df["universe"] == u], universes[u]["ppl"])
        new_dfs.append(temp_df)
        print("-" * 40)
    new_df = pd.concat(new_dfs)
    return new_df
