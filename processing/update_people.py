import pandas as pd
import numpy as np
import re, json, time


def update_ppl(universes, quotes):
    ppl = {}
    for q in quotes:
        if not q["universe"] in ppl:
            ppl[q["universe"]] = set([])
        ppl[q["universe"]] = ppl[q["universe"]].union(
            set(map(tuple, q["original_ppl"]))
        )

    for u in ppl:
        if u in universes:
            old_ppls = universes[u]["ppl"]
            new_ppls = set(map(tuple, old_ppls)).union(ppl[u])
            universes[u]["ppl"] = list(map(list, new_ppls))
        else:
            print("Adding new universe:", u)
            universes[u] = {"name": u, "ppl": list(map(list, ppl[u]))}
            print(len(ppl[u]), "new people added")
    return universes


if __name__ == "__main__":
    with open("../data/universes.json", "r") as f:
        universes = json.load(f)
    with open("../data/quotes.json", "r") as f:
        quotes = json.load(f)
    new_universes = update_ppl(universes, quotes)
    with open("../data/universes.json", "w") as f:
        json.dump(universes, f, indent=4, sort_keys=True)
